# 03. メモ画面デザイン修正 追記: メモ作成ページ追加計画 (CreateMemoView)

テンプレートの CreateMemoDialog.tsx（ダイアログ）と CreateMemoScreen.tsx（フルスクリーン）を参照し、まずはフルスクリーン型ページを Flet で実装し、その後ダイアログ型を追加する段階的導入とします。

## 目標
1. MemosView から遷移可能なメモ作成専用ページ (CreateMemoView) を追加
2. タイトル / ステータス / タグ選択 / 本文 (Markdown) / プレビュー を提供
3. 保存時に Controller の create_memo 呼び出し骨格を確立（永続化は後続）
4. キャンセル時の入力破棄確認（初期は簡易戻り）
5. 簡易 Markdown プレビュー（正規ライブラリ導入は後続）

## レイヤ設計
| レイヤ | 役割 | 方針 |
| ------ | ---- | ---- |
| View | UI構築/イベント配線 | create_memo_view.py 追加、BaseView継承 |
| Controller | 作成ユースケース呼出 | 既存 MemosController.create_memo に暫定実装 or CreateMemoController 新設 (後者検討) |
| State | 入力状態保持 | CreateMemoState dataclass 追加 |
| Presenter | 表示補助/整形 | 既存 presenter へ Markdown/バリデーション拡張（初期は最小） |

## CreateMemoState 案
- title: str = ""
- content: str = ""
- status: MemoStatus = MemoStatus.INBOX
- tags: list[str] = []
- active_tab: Literal["edit", "preview"] = "edit"

## UI構成
1. 固定ヘッダー: 戻る / タイトル / キャンセル / 保存
2. 本文エリア: 左フォーム (タイトル, ステータス, タブ: 編集/プレビュー, コンテンツ入力) + 右ヒント/タグ選択
3. レスポンシブ: モバイル1カラム → ラージスクリーン2カラム

## 簡易Markdown対応
- 見出し (#, ##, ###)
- 箇条書き (-, *)
- 太字 **text** / __text__
- 斜体 *text* / _text_
- インラインコード `code`
→ 正規表現 + 行走査。後続で markdown-it-py 等導入。

## フロー
1. MemosView の「新規メモ」クリック
2. Router で CreateMemoView 表示 (/memos/create)
3. 入力 → 保存
4. Controller 経由で作成（未実装なら警告）
5. 正常終了で MemosView に戻る & 再読込

## バリデーション/UX
- content 空 → 保存 disabled
- title 空 → "無題のメモ" 自動補完 (テンプレ互換)
- 連続クリック防止 (保存後ボタン disabled)
- 例外は notify_error() 経路

## 変更ファイル（今回）
- 新規: src/views/memos/create_memo_view.py
- 既存: src/views/memos/view.py（_handle_create_memo → /memos/create 遷移）
- 既存: src/views/memos/__init__.py（CreateMemoView export）
- 既存: src/views/layout.py（/memos/create ルート追加）

## 後続タスク
- controller.create_memo 実装（ApplicationService統合）
- ダイアログ版の追加（FAB）
- 正式 Markdown ライブラリ導入
- タグ取得を ApplicationService と統合
- 確認ダイアログ（入力破棄時）
