# Tasks: connect-settings-view-logic

<!-- OPENSPEC:START -->

- [x] 1. Create view skeleton directories and files
  - src/views/settings/{state.py,query.py,presenter.py,controller.py,view.py,components/**init**.py,components/fields/{**init**.py,boolean_field.py,choice_field.py,text_field.py,path_field.py,number_pair_field.py}}
  - Acceptance: files exist; no business logic in components
- [x] 2. Define SettingsViewState dataclass
  - Fields: loading, error_message, modified, appearance, window, database, agents
  - Acceptance: type hints complete; default initial state provided
- [x] 3. Implement Query layer
  - load_snapshot(): SettingsService.load_settings_snapshot()
  - save_snapshot(snapshot): SettingsService.save_settings_snapshot(snapshot)
  - Acceptance: unit tests with mock service pass
- [x] 4. Implement Presenter
  - present(snapshot) -> ui_state, options; provider/theme options mapping; size/position tuple 化
  - Acceptance: pure function; deterministic tests
- [x] 5. Implement Controller
  - load_initial(), save(), reset(), update handlers (theme, user_name, db_url, size, position, provider, model)
  - Immutable updates; error categorization; modified flag 管理
  - Acceptance: unit tests validate state transitions and error handling
- [x] 6. Build Field components
  - BooleanField, ChoiceField, TextField, PathField, NumberPairField (props only; passive)
  - Acceptance: no service/page.go calls; callbacks only
- [x] 7. Implement SettingsView
  - BaseView 契約; with_loading で初期ロード; コンポーネントへハンドラ注入; theme 適用
  - Acceptance: manual run shows fields; save applies YAML
- [x] 8. Wire routing
  - Add route '/settings' in router; link from home/settings menu if 存在
  - Acceptance: navigation to view works
- [x] 9. Tests
  - tests/views/settings/{test_presenter.py,test_controller.py}
  - Acceptance: run `uv run poe test` green
- [x] 10. Docs & Validation

  - Update docs/dev/views_guide.md (短い章追加) if applicable
  - Run `openspec validate connect-settings-view-logic --strict` and fix issues

<!-- OPENSPEC:END -->
