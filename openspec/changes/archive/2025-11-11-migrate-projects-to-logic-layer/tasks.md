# Tasks

順序だてた実装タスク。各ステップで UI 差分が出ないこと（ビジュアル/VM 形状/API 不変）を検証する。

1. 現状把握と影響範囲の固定

   - [x] `src/views/projects/controller.py` の Query 直接依存箇所を棚卸し
   - [x] 詳細パネルが `list_projects` の線形探索に依存している箇所を特定（暫定でフォールバック残し）
   - [x] memos の `MemosController` / `MemoApplicationPort` の最小 API を確認

2. Port 定義と依存解決戦略

   - [x] `ProjectApplicationPort`（Protocol）を `views/projects/controller.py` に暫定配置
   - [ ] 最終的な配置場所再検討（`views` から `logic/ports` などへ移設）
   - [x] View から `ProjectApplicationService.get_instance()` で取得し Controller に DI
   - [ ] Controller 内にサービス未注入時のフォールバック（遅延取得）実装
   - [ ] 単体テスト用の Port モック/スタブを作成

3. Controller 依存の置換（UI 不変）

   - [x] 一覧取得を Port 経由へ置換（`get_all_projects` / `search` / `list_by_status`）
   - [x] 詳細取得を `get_by_id` 利用＋失敗時は一覧フォールバック探索
   - [x] 例外ハンドリング（`_notify_error`）で UI snackbar 経路へ通知
   - [ ] `state.loading` 制御と with_loading 適用（非同期導入後）

4. CRUD 拡張と作成/更新統合

   - [x] `create_project` を Port (`service.create`) 利用に置換し選択状態更新
   - [x] `update_project` メソッドを新規追加（`ProjectUpdate` 構築 → `service.update`）
   - [ ] `delete_project` メソッド骨格（`service.delete` 呼び出し・一覧更新）追加
   - [ ] View 側更新 UI（編集ダイアログ等）追加（必要に応じ後続 change）

5. 非同期実行の導入（必要箇所）

   - [ ] 長時間処理（大量取得・検索）が UI ブロックしないよう AsyncExecutor を Controller 呼び出しに適用
   - [ ] `with_loading()` で `state.loading` をトグル（BaseView 実装再利用）
   - [ ] エラー時も確実に loading を解除するテスト追加

6. InMemoryQuery / サンプルデータの撤去

   - [ ] `views.sample.get_projects_for_ui` 由来のサンプルデータ使用箇所を段階的に削除
   - [ ] ダイアログ新規作成経路を完全に ApplicationService に統一（暫定マッピングロジックを Presenter/Service 側へ移設）
   - [ ] `InMemoryProjectQuery` はテスト専用である旨を README/開発ガイドへ注記

7. テスト & バリデーション

   - [ ] 単体テスト: Port モックで Controller の一覧/詳細/並び替え/エラー通知/作成/更新/削除を検証
   - [ ] 例外経路テスト: create (empty title) / update (invalid UUID) / service 例外時の snackbar 呼び出し
   - [ ] UI リグレッション: View 既存構造（レイアウト/コンポーネント階層）に差分が無いこと確認
   - [ ] OpenSpec 検証: `openspec validate migrate-projects-to-logic-layer --strict`
   - [ ] カバレッジ測定: logic + controller の CRUD 部分が閾値 (例: 80%) を満たす

8. ドキュメント

   - [ ] 開発ガイド: Projects のロジック層統合（Port/DI/エラーポリシー/CRUD）を追記
   - [ ] `views-logic-binding` / `view-state-management` との整合を明記
   - [ ] サンプルデータ撤去方針と代替（マイグレーション+シード）記述

9. フォローアップ / 改善（任意）
   - [ ] Presenter へのマッピング重複（status/日付整形）を集約し Controller から除去
   - [ ] ページング・サーバーサイドソート計画（大量件数性能）
   - [ ] エラー分類（Validation / NotFound / Unexpected）に応じた UI 表示分岐
   - [ ] Port を別モジュールへ移動し再利用性向上
