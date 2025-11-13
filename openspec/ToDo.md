# ToDo: ルーティング/ビュー/スタイルの総点検リスト

目的: 新しい `views` アーキテクチャとルーティング、各ビューの実装、Fletの非推奨API対応状況を横断的に点検し、必要な修正項目を整理します。

更新日: 2025-10-27
担当: 自動点検 (Copilot)

## **STATUS: 🎉 アプリケーション起動成功！**

✅ **完了済み** - アプリケーション正常起動 (`http://127.0.0.1:8080`)  
✅ **完了済み** - 全主要ビューのマウント動作確認済み  
✅ **完了済み** - ルーティングシステム動作確認済み  
✅ **完了済み** - `models.terminology.py`作成、import問題解消  
✅ **完了済み** - `ft.UserControl` → `ft.Control` 修正  
✅ **完了済み** - 廃止予定API警告修正: `ft.Colors` → `ft.Colors`, `ft.icons` → `ft.Icons`  

## 緊急修正が必要な問題 🚨

- [x] **MemosView Controlエラー** (優先度: 最高 → 解消済み)
  - 症状: `MemoCardList Control must be added to the page first`
  - 対応: `MemoCardList.update_memos()` にページ存在ガードを追加し未マウント時に update を抑止
  - ファイル: `src/views/memos/components/memo_card.py`, `src/views/memos/view.py`
  - フォローアップ: ライフサイクル統一 (did_mount 内で初期ロードを保証) を別タスク化予定

- [x] **TermsView SQLAlchemyエラー** (優先度: 最高 → 解消済み)
  - 症状: `'str' object has no attribute '_sa_instance_state'`
  - 対応: SQLAlchemyモデルではなく dataclass ベースのサンプル投入に切替、ORM前提処理を除去
  - ファイル: `src/views/terms/view.py`
  - フォローアップ: 実データ接続時に Repository/Service を介した型整合テスト追加

## 1) ルーティングとナビゲーション
- [x] ルート→ビューのマッピング追加 (優先度: 高) **完了**
  - 実装済み: `views/layout.py` にファクトリ方式のルーティングを追加
  - 動作確認済み: 全ビューが正常にマウント・アンマウント

- [ ] ルート定義の一元化と整合性確認
  - 現状: `src/router.py` は `views/layout.py` に委譲。OK
  - 懸念: `src/router_config.py` がレガシー(旧 `views/*` 前提)で共存。参照はされていないが混乱を招く
  - 対応案: レガシーの明確化または削除。少なくとも README/コメントで非推奨を明記
  - ファイル: `src/router_config.py`

- [ ] サイドバー項目とルートの整合性確認 (優先度: 中)
  - 現状: `views/shared/sidebar.py` のアイテムは `/memos`, `/terms`, `/weekly-review` を含む
  - 対応: 動作確認済み、但しMemosViewとTermsViewにエラーあり

## 2) Flet 非推奨APIの置換
- [x] `ft.Colors.*` → `ft.Colors.*` への移行 (優先度: 高) **完了**
  - 実施済み: `src/views/**` 内の一括置換
  - 確認済み: 置換漏れなし

- [x] `ft.icons.*` → `ft.Icons.*` への移行 (優先度: 高) **完了**
  - 実施済み: `src/views/**` 内の一括置換
  - 確認済み: 置換漏れなし

## 3) 各ビューのデータ連携とTODO
- [ ] **MemosView: Control Lifecycle修正** (優先度: 最高)
  - 現状: MemoCardListがページ追加前にupdate()を呼び出しエラー
  - 対応: ライフサイクル管理を修正、ページ追加後のupdate()確保
  - ファイル: `src/views/memos/view.py`, `src/views/memos/components/memo_card.py`

- [ ] **TermsView: サンプルデータ形式修正** (優先度: 最高)
  - 現状: 文字列サンプルデータでSQLAlchemyエラー
  - 対応: Termモデルインスタンス形式にサンプルデータを修正
  - ファイル: `src/views/terms/view.py`

- [ ] TasksView: モック→実データ配線 (優先度: 中)
  - 現状: 例外時/暫定でモックにフォールバック
  - 動作確認済み: 基本的なUIは正常動作
  - 対応: `TaskApplicationService.list_by_status()` 配線を有効化、優先度/担当/タグの取得方針を定義
  - ファイル: `src/views/tasks/view.py`
  - ファイル: `src/views/terms/view.py`

- [ ] WeeklyReviewView: 永続化 (優先度: 低-中)
  - 現状: ダッシュボード/ウィザードのUIは完備、保存はTODO
  - 対応: DB保存と履歴読み込み、グラフデータ連携
  - ファイル: `src/views/weekly_review/view.py`

## 4) ベース/共有コンポーネント
- [ ] BaseView の共通通知APIでの統一 (優先度: 低)
  - 現状: `show_snack_bar`/`show_info_snackbar`/`show_success_snackbar` が混在
  - 対応: 名前と引数の整理、ドキュメント化（self.page 依存の明確化）
  - ファイル: `src/views/shared/base_view.py`

- [x] `page_header.py` の色定義を `ft.Colors` 化 (優先度: 中 → 完了)
  - ファイル: `src/views/shared/components/page_header.py`

## 5) レガシー/重複コードの整理
- [ ] 旧 Projects 画面の整理 (優先度: 低)
  - 現状: `views/projects/view_old.py` が残存
  - 対応: 非推奨化コメント、または削除/移動

- [ ] 旧ルーター `router_config.py` の整理 (優先度: 中)
  - 詳細: 旧 `views/*` 前提のコード。現行は `views/` に統一

## 6) テスト/ドキュメント
- [ ] ナビゲーションの簡易テスト追加 (優先度: 中)
  - 例: ルート→ビュー解決のユニットテスト（`_get_view_content` のルーティング表をカバー）

- [ ] ドキュメント更新 (優先度: 低)
  - 例: `docs/app/` に新ナビゲーション/ビューの説明、`openspec/Tasks.md` の進捗同期

---
メモ: 本リストは随時更新します。簡単に直せるものから進め、変更のたびにここへ追記・完了チェックを行ってください。

## 7) Templateデザインとの整合確認 (src/views/template → src/views)

目的: Reactテンプレートの画面デザイン/UXを Flet 実装に確実に反映する。

- Memos (MemosScreen.tsx ↔ views/memos)
  - [ ] タブ別リストの完全再現 (Inbox/Active/Idea/Archive の Tabs + 各カウント)  優先: 中
    - 現状: `MemosView` はタブUIありだが、全メモを Inbox 扱い。カウントは仮ロジック。
    - 対応: ステータスごとのデータ分割、タブ切替で `MemoCardList` ソース更新。
    - ファイル: `src/views/memos/view.py`, `src/views/memos/components/action_bar.py`
  - [ ] AI提案バッジの状態別スタイル (available/pending/reviewed/failed)  優先: 中
    - 現状: 「新規」固定バッジ。
    - 対応: テンプレの Badge 色/文言を反映したステート別表示。
    - ファイル: `src/views/memos/view.py`, `src/views/memos/components/memo_card.py`
  - [ ] タグチップの色反映 (tag.color で枠線/文字色)  優先: 中
    - 現状: タグ表示なし。
    - 対応: `tags` 情報から色付き Badge を生成。
    - ファイル: `src/views/memos/components/memo_card.py`
  - [ ] 新規作成/編集ダイアログ  優先: 中
    - 現状: TODO 表示のみ。
    - 対応: Create/Edit ダイアログの実装（テンプレ相当）。
    - ファイル: `src/views/memos/components/*`, `src/views/shared/dialogs/*`
    - 仕様:
      - フィールド: タイトル(必須/最大100), 本文(Markdown/最大10k), タグ(複数/最大8), ステータス(Inbox/Active/Idea/Archive), 関連(タスク/プロジェクト任意), AI提案トグル
      - 機能: ライブMarkdownプレビュー / タイトル重複警告 / AI提案(差分ハイライト適用 or 破棄) / 楽観的保存
      - 検証: 必須(タイトル/ステータス)・最大長・タグ重複/上限・本文長 / 失敗時Snackbar
      - 保存: ApplicationService.create_memo/update_memo → 成功後リスト差分更新 + 選択維持
      - エラー: AI失敗は非同期バナー + リトライボタン
      - 新規ファイル予定: `src/views/memos/components/memo_dialogs.py`
  - [ ] 検索バー: アイコン内包・スタイル調整  優先: 低
    - 現状: 検索は機能するが見た目が異なる。
    - ファイル: `src/views/memos/components/action_bar.py`

- Terms (TermsScreen.tsx ↔ views/terms)
  - [ ] 関連アイテムセクション（関連メモ/関連タスク）  優先: 中
    - 現状: 未実装。
    - 対応: `TermDetail` 下部に関連項目リストを追加（最大3件＋残数表記、クリックで遷移）。
    - ファイル: `src/views/terms/components/term_detail.py`, `src/views/terms/view.py`
  - [ ] ステータスバッジのスタイル調整  優先: 低
    - 現状: アイコン/色は類似だがテンプレの Badge とはスタイル差。
    - ファイル: `src/views/terms/view.py`
  - [ ] 用語作成/編集ダイアログ  優先: 中
    - 現状: TODO 表示のみ。
    - 対応: `CreateTermDialog`/`EditTermDialog` 相当のダイアログ実装。
    - ファイル: `src/views/terms/components/*`, `src/views/shared/dialogs/*`
  - [ ] タブ構造の 3 状態 (approved/draft/deprecated) 再現  優先: 中
    - 現状: `SampleTermStatus` でフィルタ状態はあるが Tabs UI なし。
    - 対応: `TermStatusTabs` を再設計し、テンプレ同等の表示形式を適用。
    - ファイル: `src/views/terms/components/status_tabs.py`, `src/views/terms/view.py`
  - [ ] 検索バー (Icon + placeholder + 同義語検索)  優先: 中
    - 現状: アクションバーの検索はあるがUI/プレースホルダ差異。
    - 対応: 同義語/説明/キー含む検索ロジックを整理し placeholder 文言統一。
    - ファイル: `src/views/terms/components/action_bar.py`, `src/views/terms/view.py`
  - [ ] ステータスアイコン + 選択強調 (枠線色/背景)  優先: 低
    - 現状: `term_card` の border は選択時のみ変更、アイコンサイズ/色差異あり。
    - 対応: アイコン色・選択スタイルをテンプレ準拠に調整。
    - ファイル: `src/views/terms/components/term_card.py`
  - [ ] 詳細パネル: 説明/同義語/タグ/出典/メタ/編集/関連アイテム統合  優先: 中
    - 現状: "詳細表示は準備中" プレースホルダのみ。
    - 対応: `TermDetail` コンポーネントを新規構築し上記要素をカード構造で表示。
    - ファイル: `src/views/terms/components/term_detail.py`

- Weekly Review (WeeklyReviewScreen.tsx ↔ views/weekly_review)
  - [ ] 週次レビューチェックリスト  優先: 中
    - 現状: ダッシュボード/ウィザード中心のUI。チェックリスト未実装。
    - 対応: テンプレのチェックリストを右カラム相当へ追加。
    - ファイル: `src/views/weekly_review/components/review_components.py`, `src/views/weekly_review/view.py`
  - [ ] インボックス警告カード（要整理）  優先: 低-中
    - 現状: 未実装。
    - 対応: inbox件数>0で警告カード表示、タスク画面へ遷移アクション。
    - ファイル: `src/views/weekly_review/view.py`
  - [ ] 右カラムの「次のアクション/待機中/いつか多分」カード  優先: 中
    - 現状: 代替の統計/反省UIのみ。
    - 対応: テンプレ準拠の3カードを追加（件数/先頭3件＋もっと見る）。
    - ファイル: `src/views/weekly_review/components/review_components.py`, `src/views/weekly_review/view.py`
  - [ ] 統計カード4種（今週完了/インボックス/待機中/進行中PJ）  優先: 中
    - 現状: WeeklyStatsCard群は異なる指標（完了タスク/集中時間/達成率/新しい学び）。
    - 対応: テンプレの4カードへ差し替え、他指標は拡張モードで保持。
    - ファイル: `src/views/weekly_review/view.py`
  - [ ] someday/next/waiting ステータス取得ロジック  優先: 中
    - 現状: TaskStatus 定義と同期されておらず擬似データなし。
    - 対応: ドメインモデル拡張 or マッピング (someday→IDEA 等) を暫定実装。
    - ファイル: `models/task.py`, `src/views/weekly_review/view.py`
  - [ ] チェックリスト状態管理（完了フラグ/保存）  優先: 中
    - 現状: ウィザードトグルのみ。永続化なし。
    - 対応: 設定 or ローカルDBへ完了状態保存、再訪時復元。
    - ファイル: `src/views/weekly_review/view.py`, `logic/services/*`
  - [ ] レビュー完了アクション（完了記録 + Snackbar + 自動遷移）  優先: 低
    - 現状: プレースホルダ `show_snack_bar` のみ。
    - 対応: ReviewResultエンティティ保存→ホーム遷移。
    - ファイル: `src/views/weekly_review/view.py`, `models/review.py`
  - [ ] 過去レビュー一覧: スクロール＋詳細ダイアログ  優先: 低
    - 現状: 過去3件ハードコード。
    - 対応: Storage から取得し日付範囲/検索/詳細表示（モーダル）。
    - ファイル: `src/views/weekly_review/view.py`
  - [ ] 反省入力保存 (ReflectionCard → 永続化)  優先: 中
    - 現状: `show_snack_bar` のみでDB保存なし。
    - 対応: ApplicationService経由で保存し、ID更新/編集可能に。
    - ファイル: `src/views/weekly_review/components/review_components.py`
  - [ ] ウィザード機能 (段階的質問/進捗インジケータ)  優先: 低
    - 現状: プレースホルダ表示。
    - 対応: ステップ配列 + next/back + 途中保存。
    - ファイル: `src/views/weekly_review/components/review_wizard.py`

- Tasks (TasksScreen.tsx ↔ views/tasks)
  - [ ] タブ表示(7種)レイアウトの提供  優先: 低-中
    - 現状: Kanban ボード実装（テンプレは Tabs＋左リスト/右詳細）。
    - 対応: オプションで「クラシック(テンプレ)表示」モードを追加し切替可能にする。
    - ファイル: `src/views/tasks/view.py`, `src/views/tasks/components/*`
  - [ ] 右ペイン詳細: ステータス Select、Project/Memo リンク、タグチップ色  優先: 中
    - 現状: ダイアログ編集中心。右固定詳細パネルは未提供。
    - 対応: 詳細パネルコンポーネントを追加し、選択/更新を即時反映。
    - ファイル: `src/views/tasks/components/*`, `src/views/tasks/view.py`
  - [ ] ステータスの追加(今日/待機/期限超過/キャンセル)とカウント  優先: 中
    - 現状: TODO/PROGRESS/COMPLETED中心。
    - 対応: ドメイン側と整合しつつ拡張、ヘッダー表示の件数と同期。
    - ファイル: `src/views/tasks/components/__init__.py`, `src/views/tasks/view.py`
  - [ ] タスク検索バー (アイコン+幅/余白調整)  優先: 低
    - 現状: Kanban上部にアクションバーで検索フィールドのみ。
    - 対応: prefix_icon/placeholder をテンプレ風に変更。
    - ファイル: `src/views/tasks/components/action_bar.py`
  - [ ] タグ色付きBadge (borderColor / textColor)  優先: 低
    - 現状: モックデータ内 tags 文字列のみ使用、色スタイル未再現。
    - 対応: Tagモデルから color を取得しスタイル適用。
    - ファイル: `src/views/tasks/view.py`
  - [ ] 繰り返しタスク表示 (Badge + ルール表示)  優先: 低
    - 現状: モックに isRecurring 情報なし。
    - 対応: モデル拡張後、カード/詳細パネルに表示。
    - ファイル: `models/task.py`, `src/views/tasks/view.py`
  - [ ] 期限超過ハイライト (背景色/枠線)  優先: 低
    - 現状: Kanban列に個別スタイルなし。
    - 対応: overdue ステータス行の色分け、警告バッジ。
    - ファイル: `src/views/tasks/components/kanban_column.py`

- Tags (TagsScreen.tsx ↔ views/tags)
  - [ ] タグ詳細の関連アイテム（メモ/タスク/プロジェクト）  優先: 中
    - 現状: 一覧と簡易カードのみ。
    - 対応: 選択タグに紐づく関連リスト表示とナビゲーション。
    - ファイル: `src/views/tags/view.py`, `src/views/tags/components/*`
  - [ ] 選択タグの概要カード + 編集ボタン配置  優先: 中
    - 現状: 詳細表示未実装。
    - 対応: 上部にタグアイコン・色付き円・合計件数・編集ボタン。
    - ファイル: `src/views/tags/view.py`
  - [ ] 関連メモ/タスク/プロジェクトセクション (0件時空表示)  優先: 中
    - 現状: 未実装。
    - 対応: セクションカード化 + クリック遷移。
    - ファイル: `src/views/tags/view.py`
  - [ ] 編集ダイアログ  優先: 低-中
    - 現状: TODO。
    - 対応: `EditTagDialog` 実装 (名称/色/説明/関連再計算)。
    - ファイル: `src/views/tags/components/*`, `src/views/shared/dialogs/*`
  - [ ] 色付きカウントバッジ (合計/メモ/タスク/PJ)  優先: 低
    - 現状: 数値のみ。
    - 対応: Badge 風スタイル (枠/背景/アイコン) を適用。
    - ファイル: `src/views/tags/components/tag_card.py`
  - [ ] ナビゲーション遷移 (関連アイテムへ)  優先: 中
    - 現状: 遷移ロジック未配線。
    - 対応: Router介して `page.go()`。
    - ファイル: `src/views/tags/view.py`, `src/router.py`
- Home (HomeScreen.tsx ↔ views/home)
  - [ ] レビュー条件分岐 (overdue/todays/progress/inbox/completed)  優先: 中
    - 現状: `get_daily_review()` 固定データのみ。
    - 対応: タスク/メモ統計をもとにメッセージ・アイコン・色を動的決定。
    - ファイル: `src/views/home/view.py`, `views/sample.py`
  - [ ] Inboxメモ AIバッジ表示  優先: 低
    - 現状: バッジ無し。
    - 対応: メモステータス/AI処理状態に応じた Badge を `create_memo_item` 内へ追加。
    - ファイル: `src/views/home/view.py`
  - [ ] 統計カードの再構成 (Next Action / Inbox / Active Projects)  優先: 中
    - 現状: プロジェクト/進行中/完了/未処理メモ の4カード。
    - 対応: テンプレ構成に合わせ種別と算出ロジック差し替え。
    - ファイル: `src/views/home/view.py`
  - [ ] 最近のタスク: ステータス/タグ/優先度表示  優先: 低
    - 現状: タイトル・プロジェクト・期限のみ。
    - 対応: Taskモデル拡張後に Badge / アイコン表示。
    - ファイル: `src/views/home/view.py`, `models/task.py`
  - [ ] クイックアクション: アイコン/文言調整 (テンプレ統一)  優先: 低
    - 現状: ラベル類似、レイアウトOK。
    - 対応: テンプレの語彙/並び順に統一。
    - ファイル: `src/views/home/view.py`
  - [ ] 次のアクション/アクティブプロジェクト一覧カードの再導入  優先: 低
    - 現状: 現Flet版では未提供。
    - 対応: オプション表示 (ユーザー設定で ON/OFF) としテンプレ相当のカードを再現。
    - ファイル: `src/views/home/view.py`, `settings/manager.py`
  - [ ] タグバッジ色適用 (todaysTasks 内)  優先: 低
    - 現状: タグ表示なし。
    - 対応: Tag color 取得し border/textColor 反映。
    - ファイル: `src/views/home/view.py`
  - [ ] 新規メモボタン (右上 + navigate) デザイン差異調整  優先: 低
    - 現状: ボタンありだがスタイル差異。
    - 対応: 影/色/余白をテンプレ準拠に微調整。
    - ファイル: `src/views/home/view.py`

### ページ別進捗ステータス (2025-11-07 現在)
| Page | Missing | Partial | Done |
|------|---------|---------|------|
| Home | 動的レビュー/統計再構成/AIバッジ | クイックアクション概形 | レイアウト/基本表示 |
| Memos | ステータス別分類/AIバッジ/タグ/作成編集/Markdown拡張 | 検索・タブ骨格/詳細パネル | リスト表示基盤/選択UX |
| Terms | 詳細パネル/関連アイテム/作成編集ダイアログ | ステータスタブ/検索フィルタ | 一覧カード/絞込 |
| WeeklyReview | チェックリスト/警告カード/3分類カード/保存処理 | 統計カード/反省カード | レイアウト骨格/週計算 |
| Tasks | 7ステータス/クラシック表示/右詳細/高度検索 | CRUD(モック)/カンバン/ドラッグ移動(予定) | 基本Kanban/作成編集ダイアログ |
| Tags | 詳細パネル/関連アイテム/編集ダイアログ | 一覧カード/色チップ | 基本一覧/スナックバー |
| Projects | ステータス分類/詳細パネル/進捗バー/CRUDダイアログ | 検索バー(簡易) | 一覧カード(簡易) |
| Settings | LocalAI/通知/データ管理/危険操作/情報カード | 外観/ウィンドウ/DB設定保存 | 保存反映/リセット動作 |


- Projects (ProjectsScreen.tsx ↔ views/projects)
  - [ ] ステータス別セクション分割 (進行中/完了/保留/キャンセル)  優先: 中
    - 現状: 一覧のみ。ステータス文字列は日本語だが分類UIなし。
    - 対応: テンプレ同様に各セクションを見出し + カウント + リスト表示。
    - ファイル: `src/views/projects/view.py`
  - [ ] 進捗バー表示 (完了タスク数 / 総タスク数)  優先: 中
    - 現状: プログレス未表示。
    - 対応: `ProgressRing` もしくは `LinearProgressIndicator` で再現。
    - ファイル: `src/views/projects/components/project_card.py`
  - [ ] プロジェクト詳細パネル (説明/進捗/タスク一覧/編集ボタン)  優先: 中
    - 現状: 一覧カードのみ。
    - 対応: 選択状態で右ペインに詳細カード群を構築。
    - ファイル: `src/views/projects/view.py`
  - [ ] 検索バー (アイコン + プレースホルダ)  優先: 低
    - 現状: TextFieldのみでデザイン差異。
    - 対応: prefix_icon と余白調整。
    - ファイル: `src/views/projects/view.py`
  - [ ] ステータスバッジ色分け (active/completed/on_hold/cancelled)  優先: 低
    - 現状: ステータス文字列のみ。
    - 対応: 色・variant を状態別マッピング定義。
    - ファイル: `src/views/projects/components/project_card.py`, `src/views/projects/view.py`
  - [ ] Create/Edit ダイアログ  優先: 中
    - 現状: スナックバーのみ。
    - 対応: 専用ダイアログ (フォーム + 検証) 実装。
    - ファイル: `src/views/projects/components/project_dialogs.py`
    - 仕様:
      - フィールド: 名称(必須/最大80), ステータス(active/completed/on_hold/cancelled), 説明(最大5k), 開始日, 期限日(>=開始), タグ(複数), 優先度(low/normal/high), カラー
      - 進捗: 関連タスク完了率を読み取り専用表示 (タスク0→灰色)
      - 検証: 名称重複/必須, 日付整合性, ステータス/優先度必須
      - UX: 新規/編集タイトル切替, ステータス迅速変更ボタン, 削除二段階確認
      - 保存: ApplicationService.save_project → 差分パッチ (再ロード回避)
      - エラー: 重複はフィールド下警告 + Snackbar(error)
      - 新規ファイル予定: `src/views/projects/components/project_dialogs.py`
  - [ ] タスク一覧カード内リッチ表示 (ステータスバッジ/説明/リンクボタン)  優先: 低
    - 現状: タスク非表示。
    - 対応: 選択プロジェクトに紐づくタスクをリスト化。
    - ファイル: `src/views/projects/view.py`

- Settings (SettingsScreen.tsx ↔ views/settings)
  - [ ] ローカルAI設定セクション (自動処理/モデル選択/処理優先度)  優先: 中
    - 現状: 外観/ウィンドウ/DB のみ。
    - 対応: 新規 `LocalAISection` コンポーネント追加。
    - ファイル: `src/views/settings/components/local_ai_section.py`, `src/views/settings/view.py`
  - [ ] 通知設定 (デスクトップ/週次レビュー/AI完了)  優先: 中
    - 現状: 未実装。
    - 対応: `NotificationSection` 追加し設定保存連携。
    - ファイル: `src/views/settings/components/notification_section.py`
  - [ ] 外観設定: 表示密度オプション (compact/comfortable/spacious)  優先: 低
    - 現状: 外観セクション単純化、密度選択なし。
    - 対応: `AppearanceSection` に density 選択追加。
    - ファイル: `src/views/settings/components/appearance_section.py`
  - [ ] データ管理 (自動バックアップ/手動バックアップ/インポート・エクスポート)  優先: 中
    - 現状: DB接続のみ。
    - 対応: `DataManagementSection` 追加、設定マネージャに項目拡張。
    - ファイル: `src/views/settings/components/data_management_section.py`, `settings/manager.py`
  - [ ] 危険な操作 (全データ削除確認ダイアログ)  優先: 低
    - 現状: 未実装。
    - 対応: `ConfirmDialog` で二段階確認。
    - ファイル: `src/views/shared/dialogs/confirm_dialog.py`, `src/views/settings/view.py`
  - [ ] アプリ情報カード (Version/Build/Database/AI Model)  優先: 低
    - 現状: 未実装。
    - 対応: 読み込み時に設定/定数から表示。
    - ファイル: `src/views/settings/components/app_info_section.py`
  - [ ] 設定保存後のテーマ・ウィンドウ反映テスト  優先: 中
    - 現状: 基本反映のみ。自動処理/通知追加後の副作用未テスト。
    - 対応: pytest で設定変更→反映を検証。
    - ファイル: `tests/settings/test_settings_apply.py`

### 優先度再評価 (2025-11-07 更新)
優先度判定基準: 依存関係(前提機能) > 横断的価値(複数画面に影響) > ユーザー頻度 > 実装コスト/リスク比。

1. Projects 詳細/分類/進捗 + Create/Edit ダイアログ (中→高)  
  - 理由: タスク/タグ/ホーム統計/週次レビューの基礎。CRUD未整備で下流指標が固定化。  
2. Memos ステータス分類 + Create/Edit ダイアログ (中)  
  - 理由: Homeレビュー/AI提案/WeeklyReviewとの連携要。  
3. Tags 詳細/関連アイテム/遷移 (中)  
  - 理由: メモ/タスク/プロジェクト横断検索軸。  
4. WeeklyReview コア (チェックリスト + 3カード + ステータス取得ロジック) (中)  
  - 理由: 週次習慣価値が高く、差別化要素。  
5. Settings ローカルAI & 通知 (中)  
  - 理由: AI提案/レビューリマインダを有効化しエンゲージメント向上。  
6. Settings データ管理 (中)  
  - 理由: バックアップ/信頼性。  
7. Tasks 拡張 (7ステータス/右詳細/クラシック切替) (中-低)  
  - 理由: カンバンで最低限利用可能。詳細改善は後追い。  
8. 残余: バッジ装飾/色分け/密度/情報カード/危険操作 (低)  
  - 理由: 体験向上だがコア価値に直結しない。  

注: 週次レビュー保存/反省永続化は 1〜3 のデータ基盤後に実装した方が整合性が高い。

更新日: 2025-11-07