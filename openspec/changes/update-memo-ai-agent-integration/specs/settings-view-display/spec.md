# Capability: settings-view-display

## MODIFIED Requirements

### Requirement: SettingsView Display Fields

SettingsView は LLM Agent 設定として以下の UI フィールドを追加表示しなければならない (MUST): agent.provider (Select), agent.model (Text/Select)、agent.temperature (Slider/Number)、agent.debug_mode (Switch)。provider 選択に応じて利用可能モデルリストを Presenter から取得して表示しなければならない (SHOULD)。

#### Scenario: Agent 設定の表示

- **GIVEN** SettingsView がロード済み
- **WHEN** Agent 設定セクションを描画
- **THEN** provider/model/temperature/debug_mode の入力コンポーネントが表示され、それぞれ現在値をバインドする

### Requirement: Conditional Model Field Visibility

agent.model フィールドは provider が "custom"/"openai" 等モデル選択が必要な場合に表示し、固定プロバイダでは `readOnly` 表示に切り替えなければならない (MUST)。

#### Scenario: Provider 固有モデル

- **GIVEN** provider='openai'
- **WHEN** 設定画面を表示
- **THEN** model フィールドが選択可能になり、temperature も編集できる
