# Proposal: add-component-launcher-script

## Why

Flet 用の個別コンポーネントをアプリ全体を起動せずに検証・開発したいニーズがある。既存アプリの設定(ログ/フォント/テーマ/環境変数)を再利用しつつ、特定コンポーネントのみを速やかに起動できる統一的なスクリプトがないため、UI 開発やデバッグ効率が低下している。

## What Changes

- 新しいコンポーネント起動スクリプト (CLI) を追加 (**add-component-launcher-script**)
- スクリプトの配置: `scripts/` ディレクトリに配置し、単体起動用 CLI として提供
- 動的 import: ファイルパス or ドット区切りモジュールパス指定対応
- 既存設定再利用: `src/logging_conf.py`, `src/config.py`, `src/assets/fonts/` 等を初期化してからコンポーネント表示
- コンポーネントのインターフェイス契約定義 (候補: `create_control(page)` または `ComponentLauncherTarget` プロトコル)
- エラー時の診断出力 (インポート失敗, インターフェイス未実装, 初期化失敗)
- (オプション) 既存レイアウトラッパ適用: `src/views/layout.py` の共通構造へ組み込みテストモードを提供

## Impact

- 影響する新規 capability: `component-launcher`
- 参照コード: `src/main.py`, `src/logging_conf.py`, `src/config.py`, `src/views/layout.py`, `src/assets/fonts/`
- 開発フロー改善: 個別 UI の立ち上げ時間短縮 / 部分的リファクタ検証

## Scope

### In Scope

- CLI スクリプト仕様と要件 (引数, import 解決, 実行フロー)
- 既存設定の再利用要件 (ログ, フォント, 環境変数読み込み)
- コンポーネント契約の最小仕様策定
- 基本的なエラーハンドリング要件

### Out of Scope

- 高度なホットリロード機能
- 複数コンポーネント同時比較 UI
- プロファイリング/パフォーマンス計測機能
- Web/デスクトップ両モード同時自動選択 (初期段階では単一モード指定想定)

## Success Criteria

- 任意の `src/views/...` 内のコンポーネントをパス指定で起動できる
- ログ出力が本番アプリと同形式
- フォントが正しく適用されレンダリング崩れがない
- 失敗ケースで明確なエラーメッセージが表示され exit code ≠ 0

## Risks & Mitigations

- ファイルパスとモジュールパスの曖昧さ → 判定ルール明示 & 明確なヘルプ表示
- 既存初期化ロジック変更による重複 → 初期化関数を一箇所に抽出 (将来リファクタ) 設計で記述
- コンポーネントインターフェイス乱立 → プロトコルを提示し spec で拘束

## Dependencies

- Python importlib 標準機能のみ (追加依存なしを目標)
- 既存設定/ログ初期化関数が再利用可能であること

## Implementation Policy

- できるだけ `src/` 配下のコードは変更しない方針とする
- ただし、やむを得ず `src/` の変更が必要となる場合は、変更理由と差分案を提示し、事前にユーザーの承認を得てから着手する
- 既存の初期化ロジック (設定・ログ・フォント) の再利用を最優先し、重複実装は避ける

## Open Questions

- Web モード `poe web` と同等の起動を最初からサポートすべきか? (現時点: 先送り)
- レイアウトラップはデフォルト ON か引数で選択か? (候補: `--wrap-layout` boolean)

## Approval Needed

提案承認後に実装 (md ファイルのみ現在作成)。
