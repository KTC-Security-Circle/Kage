# 環境構築ガイド

このドキュメントでは、Kage アプリケーションの開発環境構築手順について説明します。

## 前提条件

- Windows 環境
- [uv](https://docs.astral.sh/uv/) 0.7.3 以上

## 1. リポジトリのクローン

```bash
git clone git@github.com:KTC-Security-Circle/Kage.git
cd Kage
```

## 2. poethepoet のインストール（推奨）

グローバルに poethepoet をインストールすることで、`uv run`を付けずに直接`poe`コマンドを使用できます：

```bash
# poethepoetをグローバルにインストール
uv tool install poethepoet
```

## 3. 仮想環境のセットアップと依存関係のインストール

### poethepoet タスクランナーを使用（推奨）

```bash
# 初回セットアップ（依存関係同期 + DB更新）
poe setup
```

### 手動での環境構築

```bash
# uvを使って仮想環境を作成
uv sync
```

または、pip でも環境構築できます。(※開発時は非推奨※)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

pip install .
```

## 4. pre-commit のインストール

```bash
uv run pre-commit install
```

## 5. テストの実行

変更が他の機能に影響を与えていないことを確認するために、テストを実行します。

### poethepoet を使用した実行（推奨）

```bash
# 全テスト実行
poe test

# ユニットテストのみ
poe test-unit

# カバレッジ付きテスト
poe test-cov
```

### 従来のテスト実行方法

```bash
uv run pytest
```

## 6. アプリケーションの実行

### poethepoet を使用したアプリ実行（推奨）

```bash
# 通常実行
poe app-run

# 開発モード（ホットリロード）
poe app-dev

# Webブラウザで実行
poe app-web

# Webブラウザで開発モード
poe app-web-dev
```

詳細なタスクコマンドについては[タスクランナーガイド](task_runner.md)を参照してください。

### 従来のアプリ実行方法

```bash
uv run flet run

# ホットリロードの場合
uv run flet run -rd
```

## 開発環境の設定

### 推奨されるエディタ/IDE

- Visual Studio Code（Python 拡張機能をインストール）

### デバッグ設定

Visual Studio Code でのデバッグ設定例（`.vscode/launch.json`）:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Kage",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/main.py",
      "console": "integratedTerminal"
    }
  ]
}
```

## トラブルシューティング

### よくある問題と解決策

1. **uv が見つからないエラー**
   - `uv` がインストールされていることを確認してください。`pip install uv` でインストールできます。

## 管理者向けの追加情報

### アプリケーションの構成

アプリケーションの構成を変更するには、`src/` ディレクトリ配下を編集します。

### アプリケーションビルド手順

アプリケーションのビルドは Github Actions を使用して自動化されています。`.github/workflows/build_windows.yml` ファイルを編集して、デプロイの設定を変更できます。

Github Actions から手動でビルドをトリガーして下さい。
