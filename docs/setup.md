# 環境構築ガイド

このドキュメントでは、SigotoDekiruKun アプリケーションの開発環境構築手順について説明します。

## 前提条件

- Windows環境
- [uv](https://docs.astral.sh/uv/) 0.7.3 以上

## 1. リポジトリのクローン

```bash
git git@github.com:KTC-Security-Circle/SigotoDekiruKun.git
cd SigotoDekiruKun
```

## 2. 仮想環境のセットアップと依存関係のインストール

```bash
# uvを使って仮想環境を作成
uv sync
```

または、pipでも環境構築できます。

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

pip install .
```

## 3. pre-commitのインストール

```bash
uv run pre-commit install
```

## 4. アプリケーションの実行

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
      "name": "Python: SigotoDekiruKun",
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

1. **uvが見つからないエラー**
   - `uv` がインストールされていることを確認してください。`pip install uv` でインストールできます。

## 管理者向けの追加情報

### アプリケーションの構成

アプリケーションの構成を変更するには、`src/` ディレクトリ配下を編集します。

### アプリケーションビルド手順

アプリケーションのビルドはGithub Actionsを使用して自動化されています。`.github/workflows/build_windows.yml` ファイルを編集して、デプロイの設定を変更できます。

Github Actionsから手動でビルドをトリガーして下さい。
