# Kage プロジェクト タスクランナーガイド

このプロジェクトでは [poethepoet](https://poethepoet.natn.io/) を使用してタスクランナーを実装しています。コマンド数を大幅に削減し、より使いやすく整理されました。

> ⚠️ **重要**: v0.2.0でコマンド構成を大幅に見直しました。従来のコマンドから変更があります。

## インストール・セットアップ

### poethepoet のグローバルインストール（推奨）

```bash
# poethepoetをグローバルにインストール
uv tool install poethepoet

# 初回セットアップ
poe setup
```

### ローカルプロジェクトでの使用

```bash
# uv run経由で実行
uv run poe setup
```

## 基本的な使用方法

```bash
# 利用可能なタスクの一覧表示
poe -h

# 特定のタスクのヘルプ
poe -h <command>

# タスクの実行
poe <command>
```

## 📋 利用可能なタスク一覧（17個）

### 🚀 必須コマンド

#### 環境セットアップ

| コマンド | 説明 | コマンド例 |
|---------|------|----------|
| `setup` | 初回プロジェクトセットアップ | `poe setup` |
| `sync` | 依存関係の同期 | `poe sync` |

#### アプリケーション実行

| コマンド | 説明 | コマンド例 |
|---------|------|----------|
| `run` | アプリケーション実行 | `poe run` |
| `dev` | 開発モード（ホットリロード付き） | `poe dev` |
| `web` | Web版として実行 | `poe web` |
| `cli` | CLIツール実行 | `poe cli --help` |

#### コード品質管理

| コマンド | 説明 | 実行内容 |
|---------|------|---------|
| `check` | 全品質チェック | lint + format-check + type-check |
| `fix` | コード自動修正 | lint-fix + format |

#### テスト実行

| コマンド | 説明 | コマンド例 |
|---------|------|----------|
| `test` | 全テスト実行 | `poe test` |
| `test-cov` | カバレッジ付きテスト | `poe test-cov` |

### 📚 ドキュメント・ビルド

| コマンド | 説明 | コマンド例 |
|---------|------|----------|
| `docs` | ドキュメントサーバー起動 | `poe docs` |
| `docs-build` | ドキュメントビルド | `poe docs-build` |
| `docs-deploy` | GitHub Pagesにデプロイ | `poe docs-deploy` |
| `build` | Web版ビルド | `poe build` |

### ⚙️ データベース・ユーティリティ

| コマンド | 説明 | コマンド例 |
|---------|------|----------|
| `migrate` | データベースマイグレーション | `poe migrate` |
| `db-status` | マイグレーション状態確認 | `poe db-status` |
| `clean` | キャッシュクリア | `poe clean` |

## 💡 開発ワークフローの例

### 初回セットアップ
```bash
# プロジェクトクローン後
poe setup
```

### 日常の開発作業
```bash
# 開発モードで起動
poe dev

# コード品質チェック
poe check

# 自動修正
poe fix

# テスト実行
poe test
```

### PR提出前
```bash
# 全チェック実行
poe check && poe test

# カバレッジ確認
poe test-cov
```

### ドキュメント作業
```bash
# ローカル確認
poe docs

# ビルドテスト
poe docs-build
```

## 🔄 コマンド変更点

### 削除されたコマンドと代替方法

| 旧コマンド | 新コマンド / 代替方法 |
|----------|---------------------|
| `app-run` | `poe run` |
| `app-dev` | `poe dev` |
| `app-web` | `poe web` |
| `app-web-dev` | `flet run --web -dr` |
| `app-debug` | `flet run -v` |
| `lint` | `poe check` |
| `lint-fix` | `poe fix` |
| `format` | `poe fix` |
| `format-check` | `poe check` |
| `type-check` | `poe check` |
| `docs-serve` | `poe docs` |
| `db-upgrade` | `poe migrate` |
| `db-current` | `poe db-status` |
| `build-web` | `poe build` |

### 削除されたコマンド（直接実行推奨）

| 削除されたコマンド | 代替方法 |
|------------------|---------|
| `test-unit` | `uv run pytest -m unit` |
| `test-integration` | `uv run pytest -m integration` |
| `deps-list` | `uv pip list` |
| `deps-outdated` | `uv pip list --outdated` |
| `db-downgrade` | `cd src/models && uv run alembic downgrade -1` |
| `db-history` | `cd src/models && uv run alembic history` |
| PowerShell固有コマンド | OS固有のコマンドを直接使用 |

## ❓ トラブルシューティング

### よくある問題

1. **コマンドが見つからない**
   ```bash
   # poethepoetバージョン確認
   poe --version
   
   # 利用可能なタスク確認
   poe -h
   ```

2. **依存関係エラー**
   ```bash
   # 再同期
   poe sync
   
   # キャッシュクリア
   poe clean
   ```

3. **旧コマンドが使えない**
   - 上記の「コマンド変更点」を参照
   - 多くのコマンドは `check` または `fix` に統合されました

4. **個別テスト実行**
   ```bash
   # 単体テストのみ
   uv run pytest -m unit
   
   # 特定ファイル
   uv run pytest tests/specific_test.py -v
   ```

## ⚙️ カスタマイズ

新しいタスクを追加する場合は、`pyproject.toml`の`[tool.poe.tasks]`セクションに追加：

```toml
[tool.poe.tasks]
# 既存のもの...

# カスタムタスクの例
my-task = "echo 'Custom task'"
complex-task = ["sync", "check", "test"]
```

## 📖 参考資料

- [poethepoet 公式ドキュメント](https://poethepoet.natn.io/)
- [プロジェクトアーキテクチャ](architecture-design.md)
- [セットアップガイド](setup.md)
