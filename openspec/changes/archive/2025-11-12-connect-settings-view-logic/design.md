# Design: connect-settings-view-logic

<!-- OPENSPEC:START -->

## Overview

SettingsView をレイヤー化し Logic 層 (SettingsService) を介した双方向データフローを確立する。最小責務分離: Query=取得, Presenter=UI整形, Controller=オーケストレーション, State=表示状態, View=Flet構築+ハンドラ注入, Components=受動的 Field 群。

## Data Flow

1. View.did_mount -> Controller.load_initial()
2. Controller -> Query.load_snapshot() (self.apps.settings.load_settings_snapshot)
3. Query returns raw snapshot dict -> Presenter.present(snapshot) が UI選択肢と正規化済み state payload を生成
4. Controller replaces state via immutable update (replace)
5. フィールド操作 -> Controller.update_`domain`() / update_field(path, value)
6. 保存 -> Controller.save() -> Presenter.validate?(軽量) -> self.apps.settings.save_settings_snapshot(snapshot)

## State Structure (SettingsViewState)

```text
loading: bool
error_message: str | None
appearance: { theme: str, user_name: str, last_login_user: str | None }
database: { url: str }
window: { size: tuple[int,int], position: tuple[int,int] }
agents: { provider: str, model_one_liner: str | None, provider_options: list[(value,label)], model_options: list[(value,label)] }
modified: bool  # 変更検知
```

## Presenter Responsibilities

- provider Enum → (value,label) リスト (翻訳: light/dark etc は既定)。
- agents.provider により model_options を分岐。
- size/position list[int] → tuple[int,int] (UI側で不変性強調)。
- theme 選択肢: AVAILABLE_THEMES からラベル付与。

## Error Handling

Controller 内で try/except:

- ValidationError (既知) → state.error_message に設定+SnackBar表示。
- その他 Exception → 汎用メッセージ "設定の保存に失敗しました" + loguru.exception。

View.notify_error が表示担う。

## Threading / Async

現状同期; heavy I/O なし。`with_loading` ラッパで視覚的フィードバック。Controllerはself.apps.settings経由でServiceへアクセス。後続で AsyncExecutor 導入可能な拡張ポイントを Controller に保持。

## Routing

`router.py` に `/settings` エントリ追加 (後続 tasks)。表示は Layout 経由または直接遷移。BaseView 契約を満たすため既存パターンに準拠。

## Testing Strategy

- Presenter: provider 切替時 options 生成テスト、model_options 分岐。
- Controller: load_initial populates state, update_theme toggles theme & modified, save() round-trip snapshot writes。
- Error: invalid theme raises ValidationError -> handled。

モック SettingsService (load/save snapshot が記録のみ) を注入。

## Extensibility

- EnvSettings UI: 追加 state セクション + Presenter mapping。
- Provider固有モデル増加: Presenter 内テーブル拡張のみ。
- Undo/Redo: state 履歴スタック追加。

## Trade-offs

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Snapshot辞書利用 | 継続 | Service API 既存; Presenter で正規化することで影響最小化 |
| 非同期化 | 未導入 | 現状処理軽量; 余計な抽象層を後回し |
| Immutable method | dataclasses.replace / 手動copy | pydantic BaseModel を直接 mutate せず State dataclass に値を転写 |

## Open Points

- agents.model 選択UI: 単一項目(one_liner)のみ; 拡張時は agents/models セクション増設。

<!-- OPENSPEC:END -->
