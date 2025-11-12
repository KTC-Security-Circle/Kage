# Change Proposal: layer-settings-view

## Summary

`SettingsView` を既存の単層 UI 実装から `MemosView` に倣った新レイヤー構造 (state / query / presenter / controller / view / components) に再構成し、BaseView 契約と view-\* 系仕様へ完全準拠させる提案。

## Motivation

現在の `src/views/settings/` は `view.py` + components の最小構造で、以下の課題がある:

- 状態管理が明確な dataclass と不変更新パターンに従っていない
- Controller / Presenter による責務分離がなく View が直接 UI ロジックを保持し拡張性が低い
- Query 層がないため、設定値の取得・変換ロジックが将来的に肥大化する恐れ
- BaseView 契約 (loading / error_message / lifecycle) の一貫適用が不明瞭

これらを是正し、他 View (memos) と統一した拡張容易性・テスト容易性を確保する。

## Scope

IN SCOPE:

- 新たに `state.py`, `query.py`, `presenter.py`, `controller.py` を settings 直下へ追加
- 既存 `view.py` の責務再編 (UI 構築とハンドラ注入のみ)
- Components へのハンドラ注入パターン適用
- BaseView 契約の遵守 (loading/error lifecycle)
- エラー通知/ログ出力統一 (notify_error)

OUT OF SCOPE (将来検討):

- DI コンテナ導入
- 高度な非同期実行最適化 (キャッシュ、並列ロード)
- theme トークン整理 (別変更で扱う)

## Current Settings Scope (source of truth)

現状の設定モデルは `src/settings/models.py` に定義されている。主な構成は以下の通り:

- `AppSettings`
  - `window: WindowSettings` (size, position)
  - `user: UserSettings` (theme, user_name, last_login_user)
  - `database: DatabaseSettings` (url)
  - `agents: AgentsSettings` (provider, 各 provider 用モデル指定)
- `Editable*` 各種: 画面編集用の非 frozen モデル
- `EnvSettings`: .env 取り扱い用 (画面の直接編集対象外だが関連ドキュメントとして参照)

本変更では AppSettings 系の編集体験を対象とし、`EnvSettings` は別変更で扱う想定。

## Desired Outcomes

- 設定画面の責務分離: 取得(QUERY) / 表示整形(PRESENTER) / UI イベント制御(CONTROLLER) / View とコンポーネント分離
- テスト容易性: state/presenter/controller 単体テスト追加が可能
- 一貫 API: 他 View と同形の `SettingsViewState`, `SettingsController`, `SettingsPresenter` 等

また、編集 UI の標準部品を先に定義して再利用性を高める:

- Boolean 用: `BooleanField` (トグル/スイッチ)
- 選択肢用: `ChoiceField` (ドロップダウン; Enum/列挙対応)
- 文字列用: `TextField`
- パス用: `PathField` (参照ダイアログ連携前提のプレースホルダ)
- 数値ペア用: `NumberPairField` (size/position)

## Non-Goals

- 既存他 View への横断的変更
- Repository / Service レイヤーの改修

## Guardrails

- 追加ファイルは最小限。不要な抽象化を避ける
- ビジネスロジックは Application Service 側へ委譲 (必要時 placeholder を使用)
- 不明確な設定取得は Query に集約し後続変更で拡張可能にする

## Risks

- 過剰分割による開発コスト増 → レイヤー毎に明確な役割コメント最小付与
- 将来の設定項目増加時に Query/Presenter インターフェース変更が生じる → dataclass と小さいメソッドで変更影響を局所化

## Alternatives Considered

1. 現状維持: テストと拡張難 → 不採用
2. View 内で単純な dataclass state 導入のみ: presenter/controller 不在で肥大化再発 → 不採用

## References

- `openspec/specs/views-structure/spec.md`
- `openspec/specs/view-state-management/spec.md`
- `openspec/specs/views-logic-binding/spec.md`
- `openspec/specs/base-view-contract/spec.md`
- `src/views/memos/*` 実装パターン

## Validation Plan

- 新規 spec に ADDED requirements + scenarios 定義
- `tasks.md` 実行により段階的にリファクタ -> 各段の pytest / lint パス確認
- Strict validation: `openspec validate layer-settings-view --strict` を想定構造でクリア
