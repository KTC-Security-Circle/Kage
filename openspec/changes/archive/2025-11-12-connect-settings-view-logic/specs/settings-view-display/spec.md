# Specification Delta: settings-view-display

## ADDED Requirements

### Requirement: SettingsView Display Fields

SettingsView は以下の編集フィールド群を表示しなければならない (MUST): theme, user_name, database_url, window.size, window.position, agents.provider, agents.model_one_liner (provider に応じて表示)。不要な内部フィールド (last_login_user 等直接操作不要) は読み取りのみで編集不可 (SHOULD)。

#### Scenario: Initial Fields Render

- GIVEN 初期ロード完了後
- WHEN 画面を確認
- THEN 上記フィールドが対応コンポーネント(Boolean/Choice/Text/Path/NumberPair)で表示される

### Requirement: Conditional Model Field Visibility

`agents.model_one_liner` フィールドは provider が OPENVINO もしくは GOOGLE の場合にのみ表示されなければならない (MUST)。FAKE 選択時は非表示 (MUST)。

#### Scenario: Provider Fake Hides Model

- GIVEN provider='FAKE'
- WHEN フィールド群を描画
- THEN model_one_liner 選択コンポーネントは表示されない

#### Scenario: Provider Google Shows Model

- GIVEN provider='GOOGLE'
- WHEN フィールド群を描画
- THEN model_one_liner コンポーネントが表示され options が Presenter で生成されている

### Requirement: Modified Flag Tracking

ユーザーが任意フィールドを変更した場合 state.modified が True になり、保存後 False に戻らなければならない (MUST)。

#### Scenario: Change Username Sets Modified

- GIVEN 現在 modified=False
- WHEN user_name を "Alice" に変更
- THEN state.modified=True となり保存後 False に戻る

### Requirement: Field Validation Feedback

不正入力 (空 database_url, size/position 要素数不正) はエラー表示コンポーネント( SnackBar or AlertDialog ) でユーザーに通知し、state.modified は維持されなければならない (MUST)。

#### Scenario: Empty Database URL

- GIVEN database_url を "" へ変更
- WHEN 保存を実行
- THEN エラーメッセージが表示され保存されず state.modified は True のまま

### Requirement: Theme Immediate Application

テーマ変更後 View は page.theme_mode を即時更新しなければならない (MUST)。

#### Scenario: Switch To Dark Theme

- GIVEN 現在 theme='light'
- WHEN dark を選択
- THEN page.theme_mode が DARK に更新される (再起動不要)

### Requirement: Window Size/Position Pair Handling

size, position は UI では 2 要素 NumberPairField により編集され、保存時 snapshot へ list[int] に変換されなければならない (MUST)。

#### Scenario: Edit Window Size

- GIVEN size=(1280,720)
- WHEN 幅を 1440 高さを 900 に変更
- THEN 保存処理で snapshot.window.size == [1440,900]
