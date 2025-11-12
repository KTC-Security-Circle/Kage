# Change Proposal: connect-settings-view-logic

<!-- OPENSPEC:START -->

## Summary

Settings画面(View)を未実装層構造(`state/query/presenter/controller/view/components/fields`)で導入し、ロジック層への接続は必ずアプリケーション層（self.apps.settings）経由で取得する。Controllerはself.apps.settingsからSettingsServiceへアクセスし、表示項目(テーマ/ユーザー名/DB URL/ウィンドウサイズ・位置/LLMプロバイダ/エージェントモデル選択)を調整し、双方向更新とエラーハンドリングポリシー(BaseView契約)を遵守する。

## Change ID

`connect-settings-view-logic`

## Motivation / Background

- 既存 specs: `settings-view-new-layer`, `views-logic-binding`, `views-structure` が抽象要件を提示するが SettingsView 実体が存在しない。
- `SettingsService` が snapshot load/save API を提供しているが View からの利用導線が未確立。
- 設定編集 UI は他画面に散在していないため新規構築で集中管理可能。

## Goals (Scope)

- SettingsView レイヤー構築 (state/query/presenter/controller/view/components).
- Logic層 (`SettingsService`) との対話オーケストレーション (読み込み/保存/部分更新)。
- 表示項目: AppSettings 上位の必要フィールドを UI に列挙し編集可能にする。
- 不変 state 更新と BaseView 契約適用。
- 既知/未知エラー分類表示 (SnackBar/Dialog)。
- テスト容易性 (Controller/Presenter/Service モック差し替え)。

## Non-Goals (Out of Scope)

- EnvSettings (.env) の編集UI (別変更で扱う)。
- エージェント個別モデル高度編集 (最小: provider と one_liner のモデル選択のみ)。
- 国際化/i18n。
- 高度なバリデーション (最低限: テーマ, サイズ/位置配列長, DB URL 空欄防止)。

## Success Criteria

- 画面遷移で SettingsView が表示され、初期ロードが非同期またはwith_loadingラッパ内でブロックせず完了する。
- 任意フィールド変更後に保存ボタンで YAML 更新が行われる (再起動不要)。
- テーマ切替が即時 page.theme_mode に反映。
- プロバイダ選択に応じてモデル選択フィールドの可視性/選択肢が動的変化。
- テスト: Controller 単体テストで snapshot round-trip が保証される。

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| レイヤー過剰抽象で初期実装遅延 | 最小責務+後続改善; Presenter純粋/Controller軽量 |
| 設定保存中競合 (同時編集) | 単一画面前提; 競合対応後続変更 |
| 画面更新遅延 | 必要時のみ state 差分更新; replace 利用 |
| Provider 切替時不整合 | Presenter で表示用 options 再生成, Controller 内で再ロード |

## Stakeholders

- View/UX: Flet UI 実装者
- Logic: SettingsService メンテナ
- QA: テスト作成者

## Open Questions

1. 画面遷移ルートパスは `/settings` 固定で良いか? (仮定: YES)
2. LLM provider 選択肢 (Enum 値) 以外に説明ラベル必要か? (仮定: Presenter で付与)
3. 保存後に一部値でアプリ再初期化は必要か? (仮定: 今回不要; theme は即時適用, DB URL 変更は次回起動で反映)

## Assumptions

- `SettingsService` は同期I/Oで即時戻る; 重くないため with_loading 中に処理。
- DI コンテナ未導入継続 (Serviceは直接構築または get_config_manager 経由)。

## Sequencing

1. State/Pure Presenter 契約定義
2. Query 層: Service 取得+raw snapshot受け渡し
3. Controller: ロード・保存・フィールド更新
4. Components/Fields primitive 実装
5. View: BaseView契約準拠+ハンドラ注入
6. ルーティング統合(`/settings`)
7. テスト (Presenter, Controller)
8. Docs 更新 + Spec validation

## Dependencies

- `settings-view-new-layer`/`views-logic-binding`/`views-structure` specs
- `settings_service.py` (既存)

## Validation Plan

- `openspec validate connect-settings-view-logic --strict` 実行で Requirements/Scenario 構文検証。
- Pytest: state/Controller の挙動テスト

<!-- OPENSPEC:END -->
