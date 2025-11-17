# Kage

GTD の考え方を取り入れたタスク管理デスクトップアプリケーションです。  
クリーンアーキテクチャに基づく設計で、保守性と拡張性を重視して開発されています。

## ✨ 主な機能

- **タスク管理**: 作成、編集、削除、ステータス管理
- **プロジェクト管理**: タスクの分類・整理用プロジェクト機能
- **タグ管理**: タスクの柔軟な分類システム
- **AI/Agent 統合**: LangChain/LangGraph による自動化機能（開発中）
  - 一言要約/コメント生成 Agent (provider/model 指定 & 対話モード対応)
  - クイックアクションによるテンプレートタスク生成
  - ステータス / ボード列 CLI 可視化

## 🛠️ 技術スタック

- **UI フレームワーク**: [Flet](https://flet.dev/)
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/)
- **AI/Agent**: [LangChain](https://python.langchain.com/), [LangGraph](https://python.langchain.com/docs/langgraph/)
- **パッケージ管理**: [uv](https://docs.astral.sh/uv/)
- **静的解析・フォーマッター**: [Ruff](https://docs.astral.sh/ruff/), [Pyright](https://microsoft.github.io/pyright/#/)
- **Git フック**: [pre-commit](https://pre-commit.com/)

## 🏗️ アーキテクチャ

本プロジェクトでは、保守性・拡張性を高めるためにクリーンアーキテクチャに基づいたレイヤード設計を採用しています。

- **UI Layer (views)**: Flet による UI コンポーネントと画面表示
- **Application Layer (logic/application)**: トランザクション管理と View/Service 層の橋渡し
- **Domain Service Layer (logic/services)**: ビジネスルールの実装
- **Repository Layer (logic/repositories)**: データアクセスの抽象化
- **Agent Layer (agents)**: LangChain/LangGraph による AI/自動化機能
- **Model Layer (models)**: データ構造とデータベーススキーマ

詳細な設計思想については、以下のドキュメントを参照してください。

- [アーキテクチャ設計ガイド](docs/dev/architecture-design.md)
- [Views の書き方ガイド](docs/dev/views_guide.md)
- [Agent 層 設計ガイド](docs/dev/agents_guide.md)

## 📂 ディレクトリ構造

```plain text
src
├── agents/                 # AI/LLMエージェント
│   ├── __init__.py
│   ├── base.py
│   ├── task_agents/        # タスク関連エージェント
│   └── utils.py
├── cli/                    # CLIコマンド
│   ├── commands/
│   │   ├── task.py
│   │   ├── memo.py
│   │   ├── project.py
│   │   ├── tag.py
│   │   └── agent.py
│   └── main.py
├── logic/                  # ビジネスロジック層
│   ├── application/        # Application Service層（トランザクション管理）
│   │   ├── task_application_service.py
│   │   ├── memo_application_service.py
│   │   ├── project_application_service.py
│   │   └── ...
│   ├── services/           # Domain Service層（ビジネスルール）
│   │   ├── task_service.py
│   │   ├── memo_service.py
│   │   └── ...
│   ├── repositories/       # Repository層（データアクセス）
│   │   ├── task.py
│   │   ├── memo.py
│   │   └── ...
│   ├── factory.py          # サービスファクトリ（DI）
│   └── unit_of_work.py     # トランザクション管理
├── models/                 # データモデル
│   ├── __init__.py
│   └── migrations/         # Alembicマイグレーション
│       ├── alembic.ini
│       ├── env.py
│       └── versions/
├── settings/               # 設定管理
│   ├── manager.py
│   └── models.py
├── views/                  # UI層（Flet）
│   ├── shared/             # 共通UIコンポーネント
│   ├── home/               # ホーム画面
│   ├── tasks/              # タスク管理画面
│   ├── memos/              # メモ管理画面
│   ├── projects/           # プロジェクト管理画面
│   ├── tags/               # タグ管理画面
│   ├── terms/              # 用語管理画面
│   ├── weekly_review/      # 週次レビュー画面
│   ├── layout.py           # レイアウト定義
│   └── theme.py            # テーマ設定
├── config.py               # アプリケーション設定
├── logging_conf.py         # ログ設定
├── router.py               # ルーティング
└── main.py                 # アプリケーションエントリーポイント
```

## 🚀 環境構築

環境構築の詳細については、[セットアップガイド](docs/dev/setup.md)を参照してください。

```bash
# poethepoetをグローバルにインストール（推奨）
uv tool install poethepoet

# 仮想環境の作成と依存関係のインストール
uv sync

# pre-commitフックのインストール
uv run pre-commit install
```

### Developer Docs (MkDocs)

開発者ドキュメントは MkDocs + Material で構築されています。

**推奨コマンド（poethepoet 使用）**:

- ローカル起動: `poe docs-serve`
- ビルド: `poe docs-build`
- デプロイ: `poe docs-deploy`

**従来のコマンド**:

- ローカル起動: `uv run mkdocs serve`
- ビルド: `uv run mkdocs build`
- デプロイ（GitHub Pages／gh-pages ブランチ）: CI が `main` への push で自動デプロイします。手動で行う場合は `uv run mkdocs gh-deploy --force` でも可能です。

📖 **ドキュメントサイト**: <https://ktc-security-circle.github.io/Kage/>

## 使い方

### poethepoet タスクランナーを使用した実行（推奨）

本プロジェクトでは、poethepoet を使用したタスクランナーを導入しています。詳細は[タスクランナーガイド](docs/task_runner.md)を参照してください。

```bash
# 初回セットアップ
poe setup

# アプリケーション実行
poe app-run              # 通常実行
poe app-dev              # 開発モード（ホットリロード）
poe app-web              # Webブラウザで実行

# コード品質チェック
poe check                # 品質チェック一括実行
poe fix                  # 自動修正一括実行

# テスト実行
poe test                 # 全テスト実行

# データベース操作
poe db-upgrade           # マイグレーション実行
```

### 従来の実行方法

```bash
uv run flet run

# ホットリロードの場合
uv run flet run -rd

# WEBアプリとして起動する場合
uv run flet run --web
```

### Component Launcher (単体コンポーネント検証 / Preview Strict Mode)

Flet コンポーネントを最小構成で素早くプレビューするためのランチャー `scripts/component_launcher.py` を用意しています。現在は **厳格モード** で動作し、以下の条件を満たすクラスのみ起動可能です:

1. `ft.Control` を継承している
2. `@classmethod preview(cls, ...) -> ft.Control` を実装している

`preview` メソッド内部でダミーデータ等を組み立て、テスト用インスタンスを返してください。引数注入機能（`--props` / `--props-file`）やフォールバックファクトリは削除されました。

```powershell
# 基本: クラス指定（デフォルトで簡易レイアウトに包まれて表示）
poe component --target views.memos.components.memo_card:MemoCard

# ラップを外して純粋な Control のみ表示
poe component --target views.memos.components.memo_card:MemoCard -nw
```

起動時はブラウザで表示されます（`view=WEB_BROWSER`）。ポート固定 (`8000`) のため複数同時起動には注意してください。

オプション概要（簡略化後）:

- `--target`: `module:Class` または `path/to/file.py:Class` (必須)
- `--no-wrap` / `-nw`: レイアウトラップを無効化（既定はラップ有効）

旧オプション (`--class`, `--props`, `--props-file`, `--wrap-layout`) は廃止されました。利用中のドキュメントやスクリプトからの削除を推奨します。

#### preview メソッドサンプル

```python
class MemoCard(ft.Container):
    @classmethod
    def preview(cls) -> "MemoCard":  # from __future__ import annotations 前提で文字列許容
        from datetime import datetime
        from uuid import uuid4
        from views.sample import SampleMemo
        sample = SampleMemo(
            id=uuid4(),
            title="プレビュー用メモ",
            content="ダミーコンテンツ",
            created_at=datetime.now(),
        )
        return cls(memo=sample, is_selected=True)
```

#### 移行ガイド

| 旧機能                   | 新仕様                            | 対応方法                |
| ------------------------ | --------------------------------- | ----------------------- |
| 任意ファクトリ関数起動   | サポート外                        | クラス化 + preview 追加 |
| 引数注入 (`--props` 等)  | サポート外                        | preview 内で値組み立て  |
| フォールバック探索       | サポート外                        | preview を必ず定義      |
| `--wrap-layout` 指定     | 既定ラップ / `-nw` で解除         | 必要に応じて `-nw` 使用 |
| ネイティブウィンドウ表示 | ブラウザ表示 (WEB_BROWSER) に統一 | 必要ならスクリプト改変  |

#### 拡張のヒント

- 追加表示モード（ネイティブ / ポート指定変更）が必要なら `ft.app(... view=...)` の第 3 引数を差し替え。
- コンポーネントギャラリーを作る場合は `Gallery(ft.Column)` の `preview()` で内部に各コンポーネントを並べる。
- 共通のモック生成が増えたら `src/views/_preview_data.py` のような専用ヘルパーモジュールを検討。

内部処理ではログ初期化・ページ設定（フォント/テーマ）・簡易 View ラップ（任意）を行い、本番アプリに近い外観を再現します。

## 🗂️ プロジェクト設計・開発ガイド

開発に参加する際は、以下のドキュメントを参照してください：

- [**🚀 開発者向けクイックリファレンス**](.github/QUICK_REFERENCE.md) - 新規開発者向けの要点まとめ
- [**コントリビューションガイド (CONTRIBUTING.md)**](CONTRIBUTING.md)
- [**ブランチ命名規則**](docs/dev/branch_naming.md) - ブランチ作成時の命名ルール
- [**タスクランナーガイド**](docs/dev/task_runner.md) - 開発効率化のための poe コマンド
- [環境構築ガイド](docs/dev/setup.md)
- [アーキテクチャ設計ガイド](docs/dev/architecture-design.md)
- [Views の書き方ガイド](docs/dev/views_guide.md)
- [Agent 層 設計ガイド](docs/dev/agents_guide.md)
- [Agent CLI 利用ガイド](docs/dev/cli/agent.md)
- [Task Quick Actions CLI](docs/dev/cli/task_qa.md)
- [Task Status / Board CLI](docs/dev/cli/task_status.md)

## ⚙️ 設定と環境変数

Kage では設定値を以下の優先順位で統合します：

1. 実行時環境変数 (os.environ)
2. `.env` + 既定値 (`EnvSettings` により型付与)
3. `config.yaml`（コメント保持可能な永続層）

YAML は編集コンテキストを通じて安全に更新でき、環境変数は `ENV_VARS` レジストリで一元管理されます。詳細は[設定・環境変数ガイド](docs/dev/configuration.md)を参照してください。
