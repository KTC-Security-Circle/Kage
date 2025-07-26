# Kage

FletとSQLModelを使用した、クリーンアーキテクチャに基づくデスクトップアプリケーション開発の学習・実践用プロジェクトです。

## ✨ 主な機能

- カウンター機能（サンプル実装）
- タスク管理機能（開発中）

## 🛠️ 技術スタック

- **UIフレームワーク**: [Flet](https://flet.dev/)
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/)
- **AI/Agent**: [LangChain](https://python.langchain.com/), [LangGraph](https://python.langchain.com/docs/langgraph/)
- **パッケージ管理**: [uv](https://docs.astral.sh/uv/)
- **静的解析・フォーマッター**: [Ruff](https://docs.astral.sh/ruff/)
- **Gitフック**: [pre-commit](https://pre-commit.com/)

## 🏗️ アーキテクチャ

本プロジェクトでは、保守性・拡張性を高めるためにレイヤードアーキテクチャを採用しています。

- **UI Layer (views)**: FletによるUIコンポーネントと画面表示
- **Logic Layer (logic)**: ビジネスロジック
- **Agent Layer (agents)**: LangChain/LangGraphによる自律的なタスク実行
- **Model Layer (models)**: データ構造とデータベースアクセス

詳細な設計思想については、以下のドキュメントを参照してください。

- [アーキテクチャ設計ガイド](docs/architecture-design.md)
- [Views の書き方ガイド](docs/views_guide.md)
- [Agent層 設計ガイド](docs/agents_guide.md)

## 📂 ディレクトリ構造

```
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
```

## 🤝 開発への貢献

開発に参加する際は、以下のドキュメントを一読してください。

- [**コントリビューションガイド (CONTRIBUTING.md)**](CONTRIBUTING.md)
- [環境構築ガイド](docs/setup.md)
- [アーキテクチャ設計ガイド](docs/architecture-design.md)
- [Views の書き方ガイド](docs/views_guide.md)
- [Agent層 設計ガイド](docs/agents_guide.md)

## 📄 ライセンス

このプロジェクトは MIT License のもとで公開されています。
