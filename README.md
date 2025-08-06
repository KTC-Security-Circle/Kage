# Kage

GTDの考え方を取り入れたタスク管理デスクトップアプリケーションです。  
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

## 🚀 環境構築

環境構築の詳細については、[セットアップガイド](docs/setup.md)を参照してください。

```bash
# 仮想環境の作成と依存関係のインストール
uv sync

# pre-commitフックのインストール
uv run pre-commit install
```

## 使い方

アプリケーションを実行するには：

```bash
uv run flet run

# ホットリロードの場合
uv run flet run -rd

# WEBアプリとして起動する場合
uv run flet run --web
```

## 🗂️ プロジェクト設計・開発ガイド

開発に参加する際は、以下のドキュメントを参照してください：

- [**コントリビューションガイド (CONTRIBUTING.md)**](CONTRIBUTING.md)
- [環境構築ガイド](docs/setup.md)
- [アーキテクチャ設計ガイド](docs/architecture-design.md)
- [Views の書き方ガイド](docs/views_guide.md)
- [Agent 層 設計ガイド](docs/agents_guide.md)
