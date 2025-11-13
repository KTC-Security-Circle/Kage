# Terms View - レイヤード設計

このディレクトリは、`src/views/memos`と同じレイヤー構成を採用した、用語管理ビューの実装です。

## ファイル構成

```
src/views/terms/
├── __init__.py            # TermsViewのエクスポート
├── view.py                # メインビュー（レイアウトとイベント配線）
├── controller.py          # ユースケース実行とApplicationService呼び出し
├── state.py               # 表示状態管理と派生データ
├── presenter.py           # UI表示用データ整形
├── query.py               # 検索クエリ定義と正規化
├── utils.py               # 純粋関数（フォーマット、変換、並び順）
└── components/            # 再利用可能なUIコンポーネント
    ├── __init__.py
    ├── action_bar.py      # 検索バーと作成ボタン
    ├── status_tabs.py     # ステータスフィルタタブ
    ├── term_list.py       # 用語リスト表示
    └── shared/
        ├── __init__.py
        └── constants.py   # UI定数（色、サイズ等）
```

## アーキテクチャ

### 責務分離

#### View (`view.py`)
- レイアウト構築
- コンポーネントの組み合わせ
- イベントハンドラでControllerへ委譲
- State変更後の差分更新
- BaseViewを継承し、`with_loading`/`notify_error`等を利用

#### Controller (`controller.py`)
- ユースケースメソッドの提供（`load_initial_terms`, `update_tab`, `update_search`, `select_term`）
- ApplicationServiceの呼び出し（将来実装予定）
- Stateへの状態反映と`reconcile`実行
- 検索クエリの正規化（`SearchQueryNormalizer`を使用）
- 並び順の適用（`utils`モジュールを使用）
- 例外処理とログ出力

#### State (`state.py`)
- 表示状態の保持（`current_tab`, `search_query`, `all_terms`, `selected_term_id`）
- 検索結果の保持（`search_results`）
- 派生データの計算（`derived_terms()`, `counts_by_status()`）
- 用語IDインデックスの管理（高速検索用）
- 選択状態の整合性保証（`reconcile()`）

#### Presenter (`presenter.py`)
- コンポーネント用Propsデータ生成（`create_term_card_data`, `create_term_detail_data`）
- フォーマット済みテキストの提供（`format_status_text`）
- 空状態メッセージの生成（`get_empty_message`）

#### Query (`query.py`)
- 検索クエリのデータ構造定義（`TermSearchQuery`）
- 正規化戦略（`SearchQueryNormalizer`）

#### Utils (`utils.py`)
- 日時フォーマット（`format_date`, `format_datetime`）
- 並び順ポリシー（`get_term_sort_key`, `sort_terms`）
- 安全な型変換（`safe_cast`）

### コンポーネント設計

すべてのコンポーネントは以下のパターンに従います：

1. **Props dataclass**: 不変データ（`frozen=True, slots=True`）
   - 表示に必要なデータとイベントハンドラを束ねる
   - フィールドはプリミティブ/DTO/Enum/Callable のみ

2. **UIクラス**: `ft.Control`の具体クラスを継承
   - 例: `TermActionBar(ft.Row)`, `TermList(ft.Column)`
   - `__init__(self, props: Props)` で Props から子コントロールを構築
   - `set_props(new_props)` で差分更新

3. **エラーハンドリング**: `contextlib.suppress(AssertionError)` でページ未追加時のエラーを安全にスキップ

### データフロー

```
User Action
    ↓
View (イベントハンドラ)
    ↓
Controller (ユースケース実行)
    ↓
State (状態更新 + reconcile)
    ↓
Presenter (表示用データ生成)
    ↓
Component (Props更新)
    ↓
UI更新
```

## 主な機能

- タブによるステータスフィルタリング（承認済み / 草案 / 非推奨）
- リアルタイム検索（タイトル、キー、説明、同義語で検索）
- 用語選択（将来的に詳細パネルを実装予定）
- 並び順: 更新日時降順、同一の場合はタイトル昇順

## 将来の拡張

- [ ] ApplicationService統合（データ永続化）
- [ ] 用語作成/編集ダイアログ
- [ ] 用語詳細パネル
- [ ] タグフィルタリング
- [ ] ソート順のカスタマイズ
- [ ] エクスポート機能

## 参考

このアーキテクチャは `src/views/memos/` の設計を踏襲しています。
詳細なガイドラインは `.github/copilot-instructions.md` を参照してください。
