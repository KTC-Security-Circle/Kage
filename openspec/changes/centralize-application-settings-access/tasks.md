# Tasks

進捗を反映したチェックリスト (2025-11-07 現在)。未完了項目は今後対応。

1. 設計: 共有 `SettingsApplicationService` の取得方針を整理 (シングルトン活用 + テスト用リセット案)
   - [x] シングルトン + `invalidate()` 方針決定と実装 (`BaseApplicationService.invalidate`, `SettingsApplicationService.invalidate`).
2. 既存 ApplicationService の依存棚卸し (どこでモデル名/デバッグフラグ等を参照しているか把握)
   - [x] Memo / MemoToTask / OneLiner が設定直接参照。Task/Tag/Project は非依存を確認。
3. 参照置換: ApplicationService 内設定アクセスを `SettingsApplicationService` 経由呼び出しに統一
   - [x] 対象サービスを `SettingsApplicationService` 経由へ置換 (OneLiner/Memo/MemoToTask)。
   - [x] 既存テスト (`test_one_liner_application_service.py`) を修正し `SettingsApplicationService.get_instance()` スタブ化へ移行（旧 `get_config_manager` 依存除去済み）。
4. コンストラクタ最小化: 設定値パラメータを削除し、必要なら SettingsApplicationService 受け取りのみに簡素化
   - [x] OneLiner/Memo/MemoToTask の `provider` オーバーライド引数を撤去。設定からの取得に統一（Option A）。
   - [x] テストは `SettingsApplicationService.get_instance()` のスタブ化または Agent の DI で対応。
5. 影響箇所のユニットテスト更新/追加 (設定変更が即反映されることの検証)
   - [x] 新規テスト `test_application_services_invalidate.py` 追加で `invalidate_all()` 再構築検証。
   - [x] OneLiner テスト改修完了（TypedDict 利用・スタブ差し替え・コンストラクタ変更反映）。
   - [x] Memo 例外系テスト追加（AgentError/None/想定外型 → 適切に MemoApplicationError）。
   - [x] 全テスト 339/339 PASS。
6. CLI/Views からの設定編集は既存 API を維持し回帰防止
   - [ ] 画面側/CLI の設定更新動作リグレッション未検証。次ステップで smoke テスト予定。
7. OpenSpec 検証: `openspec validate centralize-application-settings-access --strict` 実行
   - [x] 実行済み (exit code 0)。
8. ドキュメント: README/開発ガイドの設定取得ベストプラクティス更新 (必要最小限)

   - [x] 開発ガイドに「アプリ層の設定アクセス」を追加し、利用例と invalidate フローを掲載。

9. Smoke テスト/リグレッション確認 (CLI / Views で設定変更後の反映)

   - [ ] CLI: 設定変更 -> invalidate_all() -> 反映確認 (簡易テスト or 手動手順化)。[一時保留: ユーザー指示により後回し]
   - [ ] Views: 設定変更 UI (該当箇所) から変更後に OneLiner/Memo が新設定を取得する挙動を確認。 [一時保留]

10. コンストラクタ最小化フォローアップ

- [x] テスト専用の `provider` 直指定パラメータを撤去（Option A 完了）。テスト方針は Settings スタブ化/Agent DI に統一。
