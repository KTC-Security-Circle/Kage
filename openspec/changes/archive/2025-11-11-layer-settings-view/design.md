# Design: layer-settings-view

## Overview

`SettingsView` を `MemosView` と同様のレイヤー分割 (state/query/presenter/controller/view/components) に適合させ、将来の設定項目拡張 (テーマ、ウィンドウ挙動、DB 接続) を低コストにする設計。

## Layer Responsibilities

- state: 現在 UI に必要な設定値 + 共通 loading/error フラグ。不変更新で差分管理。
- query: 設定値ソース (環境変数、設定ファイル、DB) から raw 値取得。I/O を伴う処理は Application Service 経由にラップ予定。
- presenter: raw を UI 表示用構造 (選択肢リスト、ラベル、変換) に整形。複数コンポーネント間で重複する加工を一元化。
- controller: ユーザイベントに応じて state 更新 or Service 呼び出しを順序制御し、副作用境界を明確化。
- view: Flet コントロール組み立てとハンドラ注入。最小ロジック。
- components: 受け取った値とコールバックのみ使用 (Passive)。

## Data Flow

1. `did_mount()` で controller 経由 `load_settings()` を呼ぶ
2. controller が query を使い値取得 → presenter で UI 整形
3. state を不変更新 → view.update()
4. コンポーネント操作 (例: 保存ボタン) → handler → controller.save_changes()
5. 成功/失敗に応じて state 更新 + notify_error()

## Immutability Strategy

大量項目がないため標準 `dataclasses.replace` で十分。将来 100+ 項目規模なら batched diff 適用を検討。

## Error Handling

controller 内で既知/未知例外を分類し view.notify_error() 経由でユーザ通知。loguru に詳細。

## Testing Approach

- presenter: 入力 (raw settings) → 出力 (UI options) の純粋テスト
- controller: モック query/service と state 前後比較
- view: Smoke (did_mount populates controls)
- components: Boolean/Choice/NumberPair などが受動的に props を反映するか単純レンダテスト

## Extensibility

### Predefined Components (Settings)

設定編集向けに以下の再利用コンポーネントを `src/views/settings/components/fields/` 配下へ予備設置予定:

- `BooleanField`: トグル/スイッチ (値 + on_change(bool))
- `ChoiceField`: ドロップダウン (options: list[tuple[value,label]], selected, on_select(value))
- `TextField`: 単一行文字列入力 (value, on_change(str))
- `PathField`: ファイル/ディレクトリ入力 (path, on_select(new_path)) — ダイアログ連携は後続
- `NumberPairField`: 2 値 (例: size, position) (values: tuple[int,int], on_change(tuple[int,int]))

これらは Controller 経由のハンドラ注入のみを受け付け Service 直接参照を行わない。

新設定カテゴリは: state フィールド追加 → query/mapping → presenter 変換 → component 受け渡し。Controller のメソッド単位追加で既存影響局所化。

## Trade-offs

- レイヤー追加によるファイル増加 vs テスト容易性/変更コスト低減 → 採用
- query/presenter 分離は初期は簡素だが将来肥大化を防ぐ投資

## Open Questions

- Settings 保存先 (DB / file / memory) の統一 API は別変更で定義予定
- 非同期化必要な I/O 範囲 (現状軽量と想定)

## Diagram (Conceptual)

```text
Components -> View Handlers -> Controller -> (Query + Presenter) -> State -> View.update()
                                   |                              ^
                                   +---- Service (future) ---------
```
