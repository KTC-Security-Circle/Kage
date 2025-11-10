# Design: Component Launcher Script

## Context

Flet の UI コンポーネントを単体で素早く起動・検証したい。既存アプリの設定 (ログ、フォント、テーマ、環境変数) を再利用することで、表示品質と挙動の一貫性を保ったまま開発効率を高める。

## Goals / Non-Goals

- Goals
  - 既存の設定・初期化コードを再利用して、最小実装でコンポーネントを起動できる
  - ファイルパス/モジュールパス指定による動的 import をサポート
  - エラーメッセージが明確で、異常時に非ゼロ終了コードを返す
- Non-Goals
  - ホットリロードや複数コンポーネントの同時比較 UI
  - 既存アプリ本体の大規模リファクタ

## Decisions

- Dynamic Import Strategy
  - 入力形式: `path/to/module.py:ClassName` または `pkg.module:ClassName`
  - 実装: `importlib.import_module` と `importlib.util.spec_from_file_location`
  - 妥当性: `hasattr(target, ...)` で `ft.Control` サブクラスや `create_control(page)` ファクトリを受け入れる (MVP 段階はどちらか一方に絞る方針でも可)
- Flet Bootstrap
  - 既存の初期化ロジックを再利用: `logging_conf` でログ初期化、`config` で設定読み込み
  - フォント: 既存アプリが使用するフォント定義を取得し `page.fonts` に適用
  - UI 構築: `page.add(component)` で最小表示。オプションで `views/layout.py` のラッパに乗せる
- CLI インターフェイス
  - 必須: `--target` (パス形式/モジュール形式)、`--class` (省略時はデフォルト名採用も検討)
  - 任意: `--props` (JSON) でコンストラクタ引数を指定
- エラー処理
  - インポート失敗、クラス未発見、型不一致、JSON デコード失敗で明示的メッセージ

## Risks / Trade-offs

- 既存の初期化を「再利用」できない箇所があると重複コードが発生 → 将来的に初期化ヘルパへ集約
- Flet の実行モード(デスクトップ/Web)によって差異が出る → 初期段階は対象モードを固定、後続で拡張

## Migration Plan

- 完全追加 (BREAKING なし)
- 後続で `views/layout.py` ラップ有無などの拡張フラグを段階的に追加

## Open Questions

- 既存フォント設定の取得手段 (関数が無ければ最小限の重複許容)
- `ComponentLauncherTarget` の正式インターフェイス (MVP は `ft.Control` サブクラスのみに限定)
