# Proposal: Centralize Application Settings Access

## Change ID

centralize-application-settings-access

## Summary

Application 層の各サービスが個別に設定(LLM モデル選択, デバッグフラグ, DB 接続, UI テーマ等)へ直接アクセス/保持せず、`SettingsApplicationService` を単一窓口にして取得する設計へ移行する。加えて要件変更により「設定パラメータの変更時は関連 ApplicationService インスタンスを再構築する」振る舞いを定義し、動的反映と明示的再初期化を両立させる。これによりコンストラクタ引数を最小化しつつ、再構築タイミングを制御可能にする。

## Why

分散した設定参照（各 ApplicationService が個別に ConfigManager/環境変数へアクセス）により:

- 変更毎にコンストラクタ引数が肥大化し責務境界が曖昧
- 設定変更の反映タイミングが不明確でテストが難しい
- 重複コード（モデル名取得・プロバイダ選択）が散在し保守コスト増大

これを解消し設定アクセスの単一責務化と明示的な再構築手段(invalidate)を提供して拡張性とテスト容易性を向上させる。

## What Changes

- 新規 `SettingsApplicationService` を集中窓口として導入（read-only アクセサ提供）
- 全 ApplicationService から設定系コンストラクタ引数を撤去（provider/model など）
- `ApplicationServices.invalidate_all()` / `SettingsApplicationService.invalidate()` により再構築を明示的制御
- テストは Settings インスタンススタブまたは Agent DI へ統一
- ドキュメント（開発ガイド）に利用例と invalidate フローを追加
- 既存コードを Option A（設定集中 + オーバーライド撤去）へ移行

## Background / Problem

- 現状: 各 ApplicationService が必要設定を都度サービス内部で取得/保持し、生成時のパラメータが肥大化する懸念。
- 課題: 設定変更時に再インスタンス化が必要、テスト時に設定差し替えが煩雑、DI 境界が不明瞭。
- 影響: 拡張時(新しい AI モデルやデバッグオプション追加)ごとに Constructor 変更が発生し、Binary 互換性低下。

## Goals

- 設定取得を `SettingsApplicationService` 経由へ統一
- 他 ApplicationService は設定値をキャッシュせず都度問い合わせ (軽量呼び出し)
- コンストラクタ引数を "最小限 (UnitOfWorkFactory など本質的依存のみ)" へ削減
- 共有設定アクセスインスタンス (スレッド安全) を提供
- 追加 AI モデル/フラグ対応時の変更点を settings 層と settings_application_service に閉じ込める
- 設定更新イベント後に対象サービスを再構築するための標準 API (invalidate + rebuild) を提供

## Non-Goals

- 設定ファイルフォーマット変更 (YAML 構造再設計は対象外)
- 永続化戦略 (ConfigManager 自体の刷新) は行わない
- 既存 SettingsService の大幅リライトは行わない (インターフェース保持)

## Metrics / Success Criteria

- 既存 ApplicationService から設定関連コンストラクタ引数 100% 削除 or 置換
- 設定値変更後に `invalidate_application_services()` 実行で新旧インスタンス差異 (例: プロバイダ/モデル値) が即座に反映されることをテスト
- Factory 経由インスタンス生成コードの差分 (LoC 減少) を記録
- LLM モデル選択切替テスト: 旧インスタンスは古い値、新インスタンスは新しい値を参照することを検証

## High-Level Approach

1. 共有 `SettingsApplicationService` シングルトン/Factory パターン (BaseApplicationService.get_instance) を整備
2. 他 ApplicationService 内で必要設定参照関数をラップ (例: `_get_model_config()` が内部で SettingsApplicationService 呼び出し)
3. コンストラクタから設定値受け取り除去 + 参照メソッド追加
4. 設定更新時に呼べる `ApplicationServices.invalidate_all()` (仮) を追加し再構築をトリガー
5. 影響テスト更新 (再構築前後で値差異を検証)
6. バリデーション & OpenSpec strict validate

## Decision Record (Option C 採用)

最終的に以下の選択肢 C を採用した:

"設定変更後は ApplicationServices と SettingsApplicationService 双方に対して明示的な invalidate API を呼び出し、次回取得で新インスタンスを生成する。reset() はテスト用途に留め、本番コードは意図を持つ invalidate を使用する。"

選定理由:

- 意味論の明確化: reset() の曖昧さ (単なるキャッシュ全消去) を排し、設定変更イベントとの関連をコード上で表現できる
- 最小実装: invalidate_all() は内部で既存 reset() を委譲し薄いラッパーとして開始できる
- 拡張余地: 将来部分的 invalidate (例: 設定依存サービスのみ) やメトリクス計測、デバウンス制御を追加可能
- 一貫性: SettingsApplicationService の共有インスタンスも同じ概念 (invalidate→ 次回 get_instance で再生成) へ寄せる

廃案とした代替:

- A: reset() 直接利用 → 意図不透明 / 拡張困難
- B: invalidate_all() のみ (設定サービス側リセットなし) → 設定共有インスタンスの再生成保証が弱い

今後の拡張ポイント (非ゴール):

- invalidate の対象型フィルタ (e.g. invalidate(models=True, agents=True))
- 自動トリガ (設定ファイル監視) の導入
- 監査ログ/メトリクス (invalidate 呼び出し回数・所要時間)

## Risks & Mitigations

| Risk                                                 | Mitigation                                                                                      |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 呼び出し頻度増によるパフォーマンス低下               | SettingsService は軽量(YAML 読み込みは編集時のみ)のため問題低。必要なら簡易キャッシュ導入可能。 |
| 循環依存 (他 Service 内から設定経由で自分自身再参照) | アクセスは読み取りのみとし書き込みは SettingsApplicationService 経由に限定。                    |
| 共有インスタンスのテスト汚染                         | テスト毎に `get_instance` リセット or DI 差し替えヘルパを tasks.md に定義。                     |

## Open Questions

解消済み:

- シングルトン vs Factory: シングルトン + invalidate 採用 (Option C)
- テスト用 reset API: 継続保持 (内部用途) / 本番は invalidate_all()

残り:

- Hot reload (YAML 直接変更) 需要: 現段階では不要。将来拡張余地のみ記載。

## References

- `src/logic/application/settings_application_service.py`
- `src/settings/manager.py` / `SettingsService`
- 既存 OpenSpec: `logic-testing-coverage`, `memo-to-task-agent`
