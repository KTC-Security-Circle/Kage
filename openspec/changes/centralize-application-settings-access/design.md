# Design: Centralize Application Settings Access

## Architectural Overview

Application サービス間で重複する設定取得ロジックを `SettingsApplicationService` に集約し、他のサービスは都度問い合わせする Pull モデルへ移行する。要件変更により設定パラメータ更新後に **対象 ApplicationService の再構築 (re-init)** を行う公式フローを追加し、キャッシュ不要の動的取得と「明示的リセットによるクリーン状態確保」を両立する。

## Key Decisions

- シングルトン活用: `SettingsApplicationService` は `BaseApplicationService.get_instance()` を介して取得。軽量 & 設定読み取りのみなのでスレッドロック不要。
- 再構築境界: 設定変更後は `ApplicationServices.invalidate_all()` (新規) を呼び出し次回取得時に各サービスを再インスタンス化。
- 書き込み境界: 変更操作 (update\*) は設定サービスのみ。読取は read API を公開。更新後に利用層が必要なら invalidate をトリガ。
- キャッシュ戦略: 初期段階では非キャッシュ。再構築で最新値が保証される。必要なら再構築コスト低減のため軽量オブジェクトのみキャッシュ。
- DI 戦略: 他 ApplicationService の `__init__` で設定受け取る代わりにメソッド内遅延取得。テストではモック/スタブ差し替え用に `SettingsApplicationService.reset_for_test()` を提供 + invalidate ヘルパ。

## Alternatives Considered

| 代替                                    | 採用しない理由                                 |
| --------------------------------------- | ---------------------------------------------- |
| 全サービスへ ConfigManager 直接注入     | 境界が曖昧化し設定仕様変更時の影響範囲が広がる |
| イベント駆動で設定更新通知              | 複雑性過剰 (現状即時反映ニーズ小)              |
| グローバル関数 (helpers) で直接アクセス | テスタビリティ低下・拡張性不足                 |

## Data Flow

1. View/CLI が設定変更操作呼び出し (`SettingsApplicationService.update_*`).
2. 内部で `SettingsService` -> `ConfigManager.edit()` により YAML 反映。
3. 利用層が必要に応じて `ApplicationServices.invalidate_all()` を呼び再構築予約。
4. 次回 `ApplicationServices.get_service(XxxApplicationService)` 呼び出し時に新インスタンス生成し最新設定を反映。

## Thread Safety

設定読み取りは不変モデル (pydantic frozen) を参照。更新は ConfigManager の contextmanager 内で atomic に保存。現状マルチスレッド競合想定低。必要時はファイルロックを拡張余地に記載。

## Impacted Components

- `logic/application/*_application_service.py`
- Factory 生成箇所 (もし設定注入している場合)
- テストフィクスチャ (設定差し替え方法変更)

## Migration Strategy

段階的:

1. invalidate API 追加 (既存ロジック並行稼働)
2. テスト: 設定更新 → 旧インスタンス保持 →invalidate→ 新インスタンスで差異確認
3. 旧設定依存コンストラクタ引数削除 (breaking change) - OpenSpec で明示
4. ドキュメント更新: 再構築手順 (CLI / View) 追記

## OpenSpec Linkage

- Capabilities: application-settings, shared-settings-instance, constructor-minimization
