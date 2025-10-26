# ToDo: ルーティング/ビュー/スタイルの総点検リスト

目的: 新しい `views_new` アーキテクチャとルーティング、各ビューの実装、Fletの非推奨API対応状況を横断的に点検し、必要な修正項目を整理します。

更新日: 2025-10-27
担当: 自動点検 (Copilot)

## **STATUS: 🎉 アプリケーション起動成功！**

✅ **完了済み** - アプリケーション正常起動 (`http://127.0.0.1:8080`)  
✅ **完了済み** - 全主要ビューのマウント動作確認済み  
✅ **完了済み** - ルーティングシステム動作確認済み  
✅ **完了済み** - `models.terminology.py`作成、import問題解消  
✅ **完了済み** - `ft.UserControl` → `ft.Control` 修正  
✅ **完了済み** - 廃止予定API警告修正: `ft.colors` → `ft.Colors`, `ft.icons` → `ft.Icons`  

## 緊急修正が必要な問題 🚨

- [ ] **MemosView Controlエラー** (優先度: 最高)
  - 症状: `MemoCardList Control must be added to the page first`
  - 原因: MemoCardListコンポーネントがページに追加される前にupdate()を呼び出し
  - ファイル: `src/views_new/memos/components/memo_card.py`, `src/views_new/memos/view.py`

- [ ] **TermsView SQLAlchemyエラー** (優先度: 最高)
  - 症状: `'str' object has no attribute '_sa_instance_state'`
  - 原因: TermsViewでのサンプルデータが文字列だが、SQLAlchemyモデルインスタンスが期待されている
  - ファイル: `src/views_new/terms/view.py`

## 1) ルーティングとナビゲーション
- [x] ルート→ビューのマッピング追加 (優先度: 高) **完了**
  - 実装済み: `views_new/layout.py` にファクトリ方式のルーティングを追加
  - 動作確認済み: 全ビューが正常にマウント・アンマウント

- [ ] ルート定義の一元化と整合性確認
  - 現状: `src/router.py` は `views_new/layout.py` に委譲。OK
  - 懸念: `src/router_config.py` がレガシー(旧 `views/*` 前提)で共存。参照はされていないが混乱を招く
  - 対応案: レガシーの明確化または削除。少なくとも README/コメントで非推奨を明記
  - ファイル: `src/router_config.py`

- [ ] サイドバー項目とルートの整合性確認 (優先度: 中)
  - 現状: `views_new/shared/sidebar.py` のアイテムは `/memos`, `/terms`, `/weekly-review` を含む
  - 対応: 動作確認済み、但しMemosViewとTermsViewにエラーあり

## 2) Flet 非推奨APIの置換
- [x] `ft.colors.*` → `ft.Colors.*` への移行 (優先度: 高) **完了**
  - 実施済み: `src/views_new/**` 内の一括置換
  - 確認済み: 置換漏れなし

- [x] `ft.icons.*` → `ft.Icons.*` への移行 (優先度: 高) **完了**
  - 実施済み: `src/views_new/**` 内の一括置換
  - 確認済み: 置換漏れなし

## 3) 各ビューのデータ連携とTODO
- [ ] **MemosView: Control Lifecycle修正** (優先度: 最高)
  - 現状: MemoCardListがページ追加前にupdate()を呼び出しエラー
  - 対応: ライフサイクル管理を修正、ページ追加後のupdate()確保
  - ファイル: `src/views_new/memos/view.py`, `src/views_new/memos/components/memo_card.py`

- [ ] **TermsView: サンプルデータ形式修正** (優先度: 最高)
  - 現状: 文字列サンプルデータでSQLAlchemyエラー
  - 対応: Termモデルインスタンス形式にサンプルデータを修正
  - ファイル: `src/views_new/terms/view.py`

- [ ] TasksView: モック→実データ配線 (優先度: 中)
  - 現状: 例外時/暫定でモックにフォールバック
  - 動作確認済み: 基本的なUIは正常動作
  - 対応: `TaskApplicationService.list_by_status()` 配線を有効化、優先度/担当/タグの取得方針を定義
  - ファイル: `src/views_new/tasks/view.py`
  - ファイル: `src/views_new/terms/view.py`

- [ ] WeeklyReviewView: 永続化 (優先度: 低-中)
  - 現状: ダッシュボード/ウィザードのUIは完備、保存はTODO
  - 対応: DB保存と履歴読み込み、グラフデータ連携
  - ファイル: `src/views_new/weekly_review/view.py`

## 4) ベース/共有コンポーネント
- [ ] BaseView の共通通知APIでの統一 (優先度: 低)
  - 現状: `show_snack_bar`/`show_info_snackbar`/`show_success_snackbar` が混在
  - 対応: 名前と引数の整理、ドキュメント化（self.page 依存の明確化）
  - ファイル: `src/views_new/shared/base_view.py`

- [ ] `page_header.py` の色定義を `ft.Colors` 化 (優先度: 中)
  - ファイル: `src/views_new/shared/components/page_header.py`

## 5) レガシー/重複コードの整理
- [ ] 旧 Projects 画面の整理 (優先度: 低)
  - 現状: `views_new/projects/view_old.py` が残存
  - 対応: 非推奨化コメント、または削除/移動

- [ ] 旧ルーター `router_config.py` の整理 (優先度: 中)
  - 詳細: 旧 `views/*` 前提のコード。現行は `views_new/` に統一

## 6) テスト/ドキュメント
- [ ] ナビゲーションの簡易テスト追加 (優先度: 中)
  - 例: ルート→ビュー解決のユニットテスト（`_get_view_content` のルーティング表をカバー）

- [ ] ドキュメント更新 (優先度: 低)
  - 例: `docs/app/` に新ナビゲーション/ビューの説明、`openspec/Tasks.md` の進捗同期

---
メモ: 本リストは随時更新します。簡単に直せるものから進め、変更のたびにここへ追記・完了チェックを行ってください。

## 7) Templateデザインとの整合確認 (src/views/template → src/views_new)

目的: Reactテンプレートの画面デザイン/UXを Flet 実装に確実に反映する。

- Memos (MemosScreen.tsx ↔ views_new/memos)
  - [ ] タブ別リストの完全再現 (Inbox/Active/Idea/Archive の Tabs + 各カウント)  優先: 中
    - 現状: `MemosView` はタブUIありだが、全メモを Inbox 扱い。カウントは仮ロジック。
    - 対応: ステータスごとのデータ分割、タブ切替で `MemoCardList` ソース更新。
    - ファイル: `src/views_new/memos/view.py`, `src/views_new/memos/components/action_bar.py`
  - [ ] AI提案バッジの状態別スタイル (available/pending/reviewed/failed)  優先: 中
    - 現状: 「新規」固定バッジ。
    - 対応: テンプレの Badge 色/文言を反映したステート別表示。
    - ファイル: `src/views_new/memos/view.py`, `src/views_new/memos/components/memo_card.py`
  - [ ] タグチップの色反映 (tag.color で枠線/文字色)  優先: 中
    - 現状: タグ表示なし。
    - 対応: `tags` 情報から色付き Badge を生成。
    - ファイル: `src/views_new/memos/components/memo_card.py`
  - [ ] 新規作成/編集ダイアログ  優先: 中
    - 現状: TODO 表示のみ。
    - 対応: Create/Edit ダイアログの実装（テンプレ相当）。
    - ファイル: `src/views_new/memos/components/*`, `src/views_new/shared/dialogs/*`
  - [ ] 検索バー: アイコン内包・スタイル調整  優先: 低
    - 現状: 検索は機能するが見た目が異なる。
    - ファイル: `src/views_new/memos/components/action_bar.py`

- Terms (TermsScreen.tsx ↔ views_new/terms)
  - [ ] 関連アイテムセクション（関連メモ/関連タスク）  優先: 中
    - 現状: 未実装。
    - 対応: `TermDetail` 下部に関連項目リストを追加（最大3件＋残数表記、クリックで遷移）。
    - ファイル: `src/views_new/terms/components/term_detail.py`, `src/views_new/terms/view.py`
  - [ ] ステータスバッジのスタイル調整  優先: 低
    - 現状: アイコン/色は類似だがテンプレの Badge とはスタイル差。
    - ファイル: `src/views_new/terms/view.py`
  - [ ] 用語作成/編集ダイアログ  優先: 中
    - 現状: TODO 表示のみ。
    - 対応: `CreateTermDialog`/`EditTermDialog` 相当のダイアログ実装。
    - ファイル: `src/views_new/terms/components/*`, `src/views_new/shared/dialogs/*`

- Weekly Review (WeeklyReviewScreen.tsx ↔ views_new/weekly_review)
  - [ ] 週次レビューチェックリスト  優先: 中
    - 現状: ダッシュボード/ウィザード中心のUI。チェックリスト未実装。
    - 対応: テンプレのチェックリストを右カラム相当へ追加。
    - ファイル: `src/views_new/weekly_review/components/review_components.py`, `src/views_new/weekly_review/view.py`
  - [ ] インボックス警告カード（要整理）  優先: 低-中
    - 現状: 未実装。
    - 対応: inbox件数>0で警告カード表示、タスク画面へ遷移アクション。
    - ファイル: `src/views_new/weekly_review/view.py`
  - [ ] 右カラムの「次のアクション/待機中/いつか多分」カード  優先: 中
    - 現状: 代替の統計/反省UIのみ。
    - 対応: テンプレ準拠の3カードを追加（件数/先頭3件＋もっと見る）。
    - ファイル: `src/views_new/weekly_review/components/review_components.py`, `src/views_new/weekly_review/view.py`

- Tasks (TasksScreen.tsx ↔ views_new/tasks)
  - [ ] タブ表示(7種)レイアウトの提供  優先: 低-中
    - 現状: Kanban ボード実装（テンプレは Tabs＋左リスト/右詳細）。
    - 対応: オプションで「クラシック(テンプレ)表示」モードを追加し切替可能にする。
    - ファイル: `src/views_new/tasks/view.py`, `src/views_new/tasks/components/*`
  - [ ] 右ペイン詳細: ステータス Select、Project/Memo リンク、タグチップ色  優先: 中
    - 現状: ダイアログ編集中心。右固定詳細パネルは未提供。
    - 対応: 詳細パネルコンポーネントを追加し、選択/更新を即時反映。
    - ファイル: `src/views_new/tasks/components/*`, `src/views_new/tasks/view.py`
  - [ ] ステータスの追加(今日/待機/期限超過/キャンセル)とカウント  優先: 中
    - 現状: TODO/PROGRESS/COMPLETED中心。
    - 対応: ドメイン側と整合しつつ拡張、ヘッダー表示の件数と同期。
    - ファイル: `src/views_new/tasks/components/__init__.py`, `src/views_new/tasks/view.py`

- Tags (TagsScreen.tsx ↔ views_new/tags)
  - [ ] タグ詳細の関連アイテム（メモ/タスク/プロジェクト）  優先: 中
    - 現状: 一覧と簡易カードのみ。
    - 対応: 選択タグに紐づく関連リスト表示とナビゲーション。
    - ファイル: `src/views_new/tags/view.py`, `src/views_new/tags/components/*`
  - [ ] 編集ダイアログ  優先: 低-中
    - 現状: TODO。
    - 対応: `EditTagDialog` 相当の実装。
    - ファイル: `src/views_new/tags/components/*`, `src/views_new/shared/dialogs/*`