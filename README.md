# Kage

GTD（Getting Things Done）の思想を取り入れた、モダンなタスク管理デスクトップアプリケーションです。  
保守性と拡張性を重視したクリーンアーキテクチャに基づく設計で、AI 機能を活用した次世代のタスク管理を実現します。

## ✨ 特徴

- **直感的なタスク管理**: タスク、プロジェクト、タグを用いた柔軟な情報整理
- **AI 統合機能**: LLM を活用した自動化とアシスタント機能（開発中）
- **クリーンアーキテクチャ**: レイヤード設計による高い保守性と拡張性
- **モダンな UI**: Flet フレームワークによる使いやすいデスクトップアプリケーション

## 🚀 クイックスタート

```bash
# 依存関係のインストール
uv sync

# 必要であればサンプルデータの追加
uv run poe sample-data

# アプリケーションの起動（デスクトップ）
# poe タスクは `uv run poe <task>` で実行します
uv run poe run
```

詳細な環境構築手順については、[📖 ドキュメントサイト](https://ktc-security-circle.github.io/Kage/)をご覧ください。

## 🛠️ 開発

### 基本コマンド

```bash
# 開発モードで起動（ホットリロード）
uv run poe dev

# デスクトップで起動
uv run poe run

# Webで起動（ポート8080）
uv run poe web

# CLI を実行
uv run poe cli

# 依存関係の同期
uv run poe sync

# データベース移行（マイグレーション）
uv run poe migrate

# コード品質チェック / 自動修正
uv run poe check
uv run poe fix

# テスト
uv run poe test
uv run poe test-v
uv run poe test-cov

# ドキュメント
uv run poe docs
uv run poe docs-build
uv run poe docs-deploy

# ビルド（Windows 向け）
uv run poe build

# ユーティリティ
uv run poe clean
```

### 開発者向けドキュメント

本プロジェクトの詳細な設計思想、アーキテクチャ、開発ガイドラインについては、以下のドキュメントを参照してください：

- [🚀 開発者向けクイックリファレンス](.github/QUICK_REFERENCE.md)
- [コントリビューションガイド](CONTRIBUTING.md)
- [📖 ドキュメントサイト](https://ktc-security-circle.github.io/Kage/)

## 📄 ライセンス

[LICENSE](LICENSE)をご覧ください。
