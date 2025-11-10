# Specification: views-structure

<!-- OPENSPEC:START -->

## ADDED Requirements

### Requirement: Standard View Directory Layout

各ページ(View)は `src/views/<page>/view.py` をエントリーポイントとし、補助的 UI パーツは `src/views/<page>/components/` に配置しなければならない (MUST)。フォームは `components/` 下で `<entity>_form.py` の命名で管理しなければならない (SHOULD)。

#### Scenario: HomeView Directory

- GIVEN 新規 Home 画面を追加する
- WHEN ディレクトリを作成する
- THEN `src/views/home/view.py` が存在し、共通部品は `src/views/home/components/` に置かれる

### Requirement: Shared Utilities Placement

複数画面で再利用される UI コントロール/ダイアログ/Sidebar 等は `src/views/shared/` 配下に配置しなければならない (MUST)。ビジネスロジックやデータアクセスコードは shared に含めてはならない (MUST NOT)。

#### Scenario: Sidebar Placement

- GIVEN 共通 Sidebar 実装
- WHEN 共有配置を検討する
- THEN `src/views/shared/sidebar.py` に存在し、DB クエリは直接記述されない

### Requirement: Theme Centralization

テーマ/色/余白/フォント等のデザイントークンは `src/views/theme.py` に集約されなければならない (MUST)。個別コンポーネントで直接ハードコードされたカラー値は避けなければならない (MUST)。

#### Scenario: Button Color Override

- GIVEN 新規ボタン
- WHEN 色指定が必要
- THEN ハードコードせず theme 経由で参照する

### Requirement: No Business Logic In View Layer

View や components は永続化/トランザクション/AI 推論などのビジネスロジックを直接実行してはならない (MUST NOT)。必要な操作は Application Service へ委譲しなければならない (MUST)。

#### Scenario: Memo Creation From View

- GIVEN メモ作成操作
- WHEN View が処理をトリガー
- THEN MemoApplicationService.create を呼び、View 内で DB セッションを開かない

### Requirement: Naming Consistency

コンポーネントファイルは snake_case で、クラスは PascalCase を用いなければならない (MUST)。`<Entity><Action>Dialog` 等の一貫した命名で可読性を高めること (SHOULD)。

#### Scenario: TagForm Naming

- GIVEN タグ編集フォーム
- WHEN ファイルとクラスを作成
- THEN ファイル名は `tag_form.py` でクラスは `TagForm` になる

### Requirement: Layout Composition In layout.py

`src/views/layout.py` はページ全体のレイアウトを構成する責務を持ち、各ページの View クラスおよび共通コンポーネントを組み合わせて画面を構築しなければならない (MUST)。`layout.py` はビジネスロジックを含んではならない (MUST NOT)。ページ固有の UI ロジック（ハンドラ定義や state 管理）は各 `src/views/<page>/view.py` のクラスが保持し、コンポーネントへ注入しなければならない (MUST)。

#### Scenario: Compose Memos Page

- GIVEN `/memos` ルート
- WHEN レイアウトが構築される
- THEN `layout.py` は `MemosView` と `MemoList` 等のコンポーネントを組み合わせるが、Application Service を直接呼び出さない

### Requirement: BaseView Adoption

各ページの View クラスは `base-view-contract` の要件を満たし、共通の `state.loading/error_message`、`notify_error()`、`with_loading()`、`did_mount()/will_unmount()` を備えなければならない (MUST)。

#### Scenario: HomeView Implements Base Contract

- GIVEN `HomeView`
- WHEN 実装を確認
- THEN 上記の共通 API を提供し、構造と責務が統一されている

## REMOVED Requirements

(なし)

## MODIFIED Requirements

(なし)

See also: base-view-contract, view-components-guidelines (routing-and-navigation は別変更で扱うため本スコープ外)

<!-- OPENSPEC:END -->
