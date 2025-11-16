# Capability: settings-logic-integration

## MODIFIED Requirements

### Requirement: SettingsView Logic Binding via Controller

設定スナップショットには LLM エージェント向けの構造化設定 (`agent.provider`, `agent.model`, `agent.temperature`, `agent.debug_mode`) を含めなければならない (MUST)。Controller は load/save 双方でこれらフィールドを扱い、更新時に SettingsService 経由で永続化しなければならない (MUST)。

#### Scenario: Agent 設定を保存

- **GIVEN** ユーザーがモデルを "gpt-4o"、debug_mode を True に変更
- **WHEN** SettingsController.save_settings を実行
- **THEN** snapshot.agent.\* が更新され、SettingsService.save_settings_snapshot に渡される

### Requirement: Presenter Isolation

Presenter は agent 設定を UI コンポーネントへ供給するため、provider/model の候補やデバッグモードの説明テキストを生成しなければならない (MUST)。

#### Scenario: Provider 候補の提示

- **GIVEN** 設定モジュールに `AgentProvider` Enum が定義されている
- **WHEN** Presenter.present(snapshot) を呼ぶ
- **THEN** provider_options に Enum 値/表示名のリストが含まれ、UI がセレクトボックス表示できる
