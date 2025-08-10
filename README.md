# Kage

GTD の考え方を取り入れたタスク管理デスクトップアプリケーションです。  
クリーンアーキテクチャに基づく設計で、保守性と拡張性を重視して開発されています。

## ✨ 主な機能

- **タスク管理**: 作成、編集、削除、ステータス管理
- **プロジェクト管理**: タスクの分類・整理用プロジェクト機能
- **タグ管理**: タスクの柔軟な分類システム
- **AI/Agent 統合**: LangChain/LangGraph による自動化機能（開発中）

## 🛠️ 技術スタック

- **UI フレームワーク**: [Flet](https://flet.dev/)
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/)
- **AI/Agent**: [LangChain](https://python.langchain.com/), [LangGraph](https://python.langchain.com/docs/langgraph/)
- **パッケージ管理**: [uv](https://docs.astral.sh/uv/)
- **静的解析・フォーマッター**: [Ruff](https://docs.astral.sh/ruff/), [Pyright](https://microsoft.github.io/pyright/#/)
- **Git フック**: [pre-commit](https://pre-commit.com/)

## 🏗️ アーキテクチャ

本プロジェクトでは、保守性・拡張性を高めるためにレイヤードアーキテクチャを採用しています。

- **UI Layer (views)**: Flet による UI コンポーネントと画面表示
- **Logic Layer (logic)**: ビジネスロジック
- **Agent Layer (agents)**: LangChain/LangGraph による自律的なタスク実行
- **Model Layer (models)**: データ構造とデータベースアクセス

詳細な設計思想については、以下のドキュメントを参照してください。

- [アーキテクチャ設計ガイド](docs/architecture-design.md)
- [Views の書き方ガイド](docs/views_guide.md)
- [Agent 層 設計ガイド](docs/agents_guide.md)

## 📂 ディレクトリ構造

```plain text
src
├── agents/
│   ├── __init__.py
│   ├── tools/              # 共通ツール
│   └── [agent_name]/       # 特定のエージェント
│       ├── agent.py
│       └── graph.py
├── logic/
│   ├── __init__.py
│   ├── repositories/       # データアクセス層 (DB操作)
│   │   └── task_repository.py
│   └── services/           # ビジネスロジック層
│       └── task_service.py
├── models/
│   ├── __init__.py
│   └── task.py             # SQLModelのテーブル定義
├── views/
│   ├── __init__.py
│   ├── shared/             # 共通UIコンポーネント
│   └── [feature_name]/     # 機能ごとのView
│       ├── view.py
│       └── components.py
└── main.py                 # アプリケーションのエントリーポイント
```

## 🚀 環境構築

環境構築の詳細については、[セットアップガイド](docs/setup.md)を参照してください。

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

- ローカル起動: `uv run mkdocs serve`
- ビルド: `uv run mkdocs build`
- デプロイ（GitHub Pages／gh-pages ブランチ）: CI が `main` への push で自動デプロイします。手動で行う場合は `uv run mkdocs gh-deploy --force` でも可能です。

サイト URL: <https://ktc-security-circle.github.io/Kage/>

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

## 🗂️ プロジェクト設計・開発ガイド

開発に参加する際は、以下のドキュメントを参照してください：

- [**🚀 開発者向けクイックリファレンス**](.github/QUICK_REFERENCE.md) - 新規開発者向けの要点まとめ
- [**コントリビューションガイド (CONTRIBUTING.md)**](CONTRIBUTING.md)
- [**ブランチ命名規則**](docs/branch_naming.md) - ブランチ作成時の命名ルール
- [**タスクランナーガイド**](docs/task_runner.md) - 開発効率化のための poe コマンド
- [環境構築ガイド](docs/setup.md)
- [アーキテクチャ設計ガイド](docs/architecture-design.md)
- [Views の書き方ガイド](docs/views_guide.md)
- [Agent 層 設計ガイド](docs/agents_guide.md)
