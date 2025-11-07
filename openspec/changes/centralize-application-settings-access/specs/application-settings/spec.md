# Capability: Application Settings Centralization

## ADDED Requirements

### Requirement: Unified settings retrieval via SettingsApplicationService

`SettingsApplicationService` MUST expose read-only accessors for all configuration domains required by other Application Services (agents models, user/theme, database url, window settings) so that no other Application Service reads `ConfigManager` or `SettingsService` directly.

#### Scenario: Retrieve agent model name

Given an ApplicationService needing the current one_liner agent model
When it requests `SettingsApplicationService.get_agents_settings().get_model_name("one_liner")`
Then it receives the configured model enum or string without accessing ConfigManager directly
And no constructor parameters were required for model selection.

#### Scenario: Theme read after update

Given the theme was changed via `SettingsApplicationService.update_user_settings(theme="dark")`
When another ApplicationService calls `get_user_settings()`
Then it observes `theme == "dark"` without reinflating its own instance.

### Requirement: No direct config dependencies in other ApplicationServices

All non-settings Application Services MUST remove any constructor props representing settings (LLM model names, debug flags) and MUST obtain those values lazily via methods calling SettingsApplicationService.

#### Scenario: Constructor minimization

Given a TaskApplicationService previously accepted `model_name` in its constructor
When the change is applied
Then its constructor no longer has a `model_name` parameter
And runtime behaviour remains equivalent by calling SettingsApplicationService.

### Requirement: Read operations remain lightweight

Reading settings through SettingsApplicationService MUST not introduce noticeable latency (>5ms overhead per call on average baseline environment) compared with previous direct access pattern.

#### Scenario: Performance smoke

Given a loop of 100 sequential `get_user_settings()` calls
When measured
Then cumulative overhead attributable to the centralization layer is insignificant (<500ms total) vs baseline.

## MODIFIED Requirements

### Requirement: Settings updates SHALL require explicit re-instantiation trigger

Previous behaviour aiming for automatic propagation without re-instantiation is replaced: services MUST continue to use prior configuration until an explicit invalidation trigger (`ApplicationServices.invalidate_all()` or equivalent) is invoked. After invalidation, next acquisition (`get_service(...)`) MUST yield a freshly constructed instance reflecting new settings.

#### Scenario: DB URL change requires invalidate

Given `update_database_settings(url="sqlite:///new.db")` is called
And no invalidation has yet occurred
When an existing ApplicationService instance creates a Repository
Then it still uses the old URL
When `ApplicationServices.invalidate_all()` is invoked
And the service is re-acquired
Then the new Repository uses `sqlite:///new.db`.

## REMOVED Requirements

None.
