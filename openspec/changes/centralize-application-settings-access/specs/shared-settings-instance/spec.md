# Capability: Shared Settings Service Instance

## ADDED Requirements

### Requirement: Provide shared instance acquisition

Other ApplicationServices MUST acquire a shared `SettingsApplicationService` instance through a standard accessor (e.g., `SettingsApplicationService.get_instance()`) ensuring consistent state.

#### Scenario: Multiple services reuse shared instance

Given TaskApplicationService and MemoApplicationService both call `SettingsApplicationService.get_instance()`
When each retrieves user settings
Then both operate on the same underlying settings snapshot (updated on write operations).

### Requirement: Safe test resetting

A test-only reset mechanism MUST exist to clear or reinitialize the shared instance without affecting production usage.

#### Scenario: Test resets service

Given a test modifies theme to "dark"
When it invokes `SettingsApplicationService.reset_for_test()` and sets theme to "light"
Then subsequent calls observe "light" and no residue from prior test remains.

## MODIFIED Requirements

### Requirement: Instance lifecycle SHALL support invalidation & rebuild

Prior implicit construction patterns are replaced with explicit `get_instance()` usage plus an invalidation API. Callers MUST prefer the shared accessor for normal use and MUST invoke the invalidation trigger to force re-instantiation after settings changes.

#### Scenario: Invalidation triggers new shared instance

Given a shared instance is in use
And a settings update occurs
When tests (or runtime) call `SettingsApplicationService.invalidate_for_settings_change()` (name TBD)
Then subsequent `get_instance()` returns a new object (identity differs) reflecting updated settings.

## REMOVED Requirements

None.
