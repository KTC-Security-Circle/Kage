# Capability: Constructor Minimization

## ADDED Requirements

### Requirement: Remove settings parameters from constructors

ApplicationServices MUST not accept settings (e.g., model name, debug flags) as constructor parameters. They MUST retrieve them lazily via `SettingsApplicationService` inside operational methods.

#### Scenario: Remove model param

Given `MemoToTaskApplicationService(model_name=...)` existed previously
When applying the change
Then the constructor no longer accepts `model_name`
And internal code calls `SettingsApplicationService.get_agents_settings().get_model_name("memo_to_task")` as needed.

### Requirement: Maintain backward-compatible behaviour

Runtime behaviour MUST be equivalent from caller perspective; only wiring changes internally.

#### Scenario: CLI continues to work

Given CLI commands that didn't pass settings explicitly
When running after the change
Then they continue to function with settings read from central service.

## MODIFIED Requirements

### Requirement: Factory adjustments SHALL integrate invalidation

Factories creating ApplicationServices MUST be updated to stop passing removed settings parameters; build signatures simplified. Factories MUST recreate fresh instances after a global invalidation signal instead of returning cached ones.

#### Scenario: Factory recreates after invalidation

Given `Factory.create_memo_to_task_service()` returned an instance prior to settings change
When settings are updated and invalidation is triggered
And `Factory.create_memo_to_task_service()` is called again
Then it returns a new instance (different identity) using updated settings.

## REMOVED Requirements

None.
