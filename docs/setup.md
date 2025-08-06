# 環境構築ガイド

このドキュメントでは、Kage アプリケーションの開発環境構築手順について説明します。

## クイックスタート

経験豊富な開発者向けの最短手順：

```bash
# 1. uvのインストール（Windows PowerShell）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. プロジェクトのクローンと環境構築
git clone git@github.com:KTC-Security-Circle/Kage.git
cd Kage
uv sync
uv run alembic upgrade head
uv run pre-commit install

# 3. アプリケーション起動
uv run flet run -rd
```

## 前提条件

### 必須要件

- **OS**: Windows 10/11（推奨）
- **Python**: 3.12 以上（Python 3.12.5 推奨）
- **パッケージマネージャー**: [uv](https://docs.astral.sh/uv/) 0.7.3 以上（現在 0.7.3 でテスト済み）

### 推奨ツール

- **エディタ**: [Visual Studio Code](https://code.visualstudio.com/)
  - Python 拡張機能
  - Pylance 拡張機能
- **Git**: バージョン管理用

## uv のインストール

### Windows での uv インストール

最も簡単な方法は PowerShell を使用することです：

```powershell
# PowerShellで実行（管理者権限不要）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### その他のインストール方法

```bash
# pipxを使用（Python環境が既にある場合）
pipx install uv

# pipを使用（非推奨）
pip install uv

# WinGetを使用
winget install --id=astral-sh.uv -e
```

### インストール確認

```bash
uv --version
# 出力例: uv 0.7.3 (3c413f74b 2025-05-07)
```

## 1. リポジトリのクローン

```bash
git clone git@github.com:KTC-Security-Circle/Kage.git
cd Kage
```

## 2. Python の管理とインストール

uv は自動的に Python バージョンを管理できます：

```bash
# プロジェクトで必要なPython（3.12以上）を自動インストール
uv python install

# 利用可能なPythonバージョンを確認
uv python list

# 特定のバージョンをインストール（必要に応じて）
uv python install 3.12
```

## 3. 仮想環境のセットアップと依存関係のインストール

```bash
# 仮想環境の作成と依存関係の一括インストール
uv sync
```

**注意**: `uv sync`は以下を自動的に実行します：

- 仮想環境の作成（`.venv`ディレクトリ）
- 本番環境用依存関係のインストール
- 開発環境用依存関係のインストール（`[tool.uv.dev-dependencies]`）
- プロジェクト自体を editable mode でインストール

### 依存関係ツリーの確認

```bash
# インストールされた依存関係を確認
uv tree
```

現在のプロジェクトは以下の主要な依存関係を使用しています：

- **Flet**: 0.27.6（UI フレームワーク）
- **LangChain/LangGraph**: AI/Agent 機能
- **SQLModel**: ORM
- **Alembic**: データベースマイグレーション
- **開発ツール**: Ruff, Pyright, pytest, pre-commit

### レガシー pip での環境構築（非推奨）

通常の開発では推奨されませんが、必要に応じて：

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install .
```

## 4. データベースの初期化

```bash
# データベースマイグレーションの実行
uv run alembic upgrade head
```

## 5. pre-commit のインストール

```bash
uv run pre-commit install
```

## 6. 環境構築の確認

すべての設定が正しく完了したことを確認：

```bash
# プロジェクトの整合性チェック
uv run poe check

# またはステップごとに確認
uv run ruff format src        # コードフォーマット
uv run ruff check src --fix   # リント・自動修正
uv run pyright src           # 型チェック
```

## 7. テストの実行

変更が他の機能に影響を与えていないことを確認するために、テストを実行します。

```bash
# 全テストの実行
uv run pytest

# カバレッジ付きテスト実行
uv run pytest --cov=src --cov-report=html

# 特定のテストファイルのみ実行
uv run pytest tests/test_specific.py
```

## 8. アプリケーションの実行

```bash
# デスクトップアプリとして起動
uv run flet run

# ホットリロード付きで起動（開発時推奨）
uv run flet run -rd

# Webアプリとして起動
uv run flet run --web
uv run flet run --web --port 8550  # ポート指定

# 特定のファイルを指定して起動
uv run flet run src/main.py
```

### 起動方法の詳細

- **デスクトップモード**: ネイティブ Windows アプリとして起動
- **ホットリロード**: ファイル変更時に自動で再読み込み
- **Web モード**: ブラウザでアクセス可能（フラグなしの場合はランダムポート）

### VS Code タスクを使用した起動

プロジェクトには以下の VS Code タスクが設定済みです：

```bash
# タスクランナーで環境セットアップ
Ctrl+Shift+P → "Tasks: Run Task" → "setup project"
```

利用可能なタスク：

- `uv sync`: 依存関係の同期
- `alembic upgrade`: データベースマイグレーション
- `setup project`: 上記 2 つの順次実行

## 開発環境の設定

### 推奨されるエディタ/IDE

#### Visual Studio Code（推奨）

必須拡張機能：

- **Python** (`ms-python.python`)
- **Pylance** (`ms-python.vscode-pylance`)

推奨拡張機能：

- **Ruff** (`charliermarsh.ruff`)

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
      "console": "integratedTerminal",
      "python": "${workspaceFolder}/.venv/Scripts/python.exe"
    },
    {
      "name": "Python: Kage (Web)",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/src/main.py",
      "args": ["--web"],
      "console": "integratedTerminal",
      "python": "${workspaceFolder}/.venv/Scripts/python.exe"
    }
  ]
}
```

### 開発ワークフロー

#### 日常的な開発作業

```bash
# 新しい依存関係の追加
uv add パッケージ名

# 開発用依存関係の追加
uv add --dev パッケージ名

# 依存関係の削除
uv remove パッケージ名

# ロックファイルの更新
uv lock

# 環境の再同期
uv sync
```

#### コード品質チェック

```bash
# すべてのコード品質チェックを実行
uv run poe check

# 個別実行
uv run ruff format src        # フォーマット
uv run ruff check src --fix   # リント（自動修正付き）
uv run pyright src           # 型チェック
```

## トラブルシューティング

### よくある問題と解決策

#### 1. uv が見つからないエラー

**症状**: `'uv' is not recognized as an internal or external command`

**解決策**:

```bash
# uvが正しくインストールされているか確認
where uv

# PATHに追加されていない場合、環境変数の確認
echo $env:PATH  # PowerShell
```

#### 2. Python バージョンの問題

**症状**: `Python 3.12 or higher is required`

**解決策**:

```bash
# uvでPythonを管理
uv python install 3.12
uv python pin 3.12

# 現在のPythonバージョン確認
uv run python --version
```

#### 3. 依存関係の競合

**症状**: 依存関係解決エラーや古いパッケージの警告

**解決策**:

```bash
# ロックファイルを削除して再生成
rm uv.lock
uv sync

# キャッシュをクリア
uv cache clean
```

#### 4. pre-commit フックエラー

**症状**: コミット時に pre-commit フックが失敗

**解決策**:

```bash
# pre-commitを再インストール
uv run pre-commit uninstall
uv run pre-commit install

# 全ファイルに対してpre-commitを実行
uv run pre-commit run --all-files
```

#### 5. Flet アプリの起動エラー

**症状**: `flet: command not found` や Flet クライアントのダウンロードエラー

**解決策**:

```bash
# uvを使用してFletを実行
uv run flet run src/main.py

# Fletクライアントを手動でダウンロード
uv run python -c "import flet as ft; ft.app(lambda page: None)"
```

#### 6. データベース関連のエラー

**症状**: SQLite ファイルが見つからない、またはマイグレーションエラー

**解決策**:

```bash
# データベースファイルの確認
ls storage/data/

# マイグレーションの状況確認
uv run alembic current

# 強制的にマイグレーション実行
uv run alembic upgrade head
```

### パフォーマンス最適化

#### uv の高速化設定

```bash
# uvの並列処理を最大化
export UV_CONCURRENT_DOWNLOADS=10
export UV_CONCURRENT_BUILDS=4

# または .uvrc ファイルに設定
echo "concurrent-downloads = 10" > .uvrc
echo "concurrent-builds = 4" >> .uvrc
```

## 管理者向けの追加情報

### プロジェクト構成

```text
Kage/
├── .vscode/              # VS Code設定
│   ├── tasks.json       # タスク定義
│   ├── settings.json    # エディタ設定
│   └── extensions.json  # 推奨拡張機能
├── docs/                # ドキュメント
├── src/                 # アプリケーションソースコード
│   ├── agents/         # AI/Agentモジュール
│   ├── logic/          # ビジネスロジック
│   ├── models/         # データモデル
│   ├── views/          # UI層
│   └── main.py         # アプリケーションエントリーポイント
├── tests/              # テストコード
├── storage/            # データベース・ファイルストレージ
├── pyproject.toml      # プロジェクト設定・依存関係
├── uv.lock            # 依存関係のロックファイル
└── alembic.ini        # データベースマイグレーション設定
```

### 依存関係管理

#### 本番環境デプロイ用

```bash
# 本番環境用の依存関係のみインストール
uv sync --no-dev

# requirements.txtの生成（必要に応じて）
uv export --no-dev -o requirements.txt
```

#### 新しい依存関係の追加

```bash
# 本番依存関係
uv add 新しいパッケージ

# 開発依存関係
uv add --dev 新しい開発ツール

# オプショナル依存関係
uv add --optional feature 新しいパッケージ
```

### CI/CD との統合

#### GitHub Actions での設定例

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
        with:
          version: "0.7.3"
      - run: uv sync
      - run: uv run pytest
      - run: uv run poe check
```

### アプリケーションビルド手順

#### 開発版ビルド

```bash
# デスクトップアプリケーションのパッケージ化
uv run flet pack src/main.py

# 配布可能なexeファイルの生成
uv run flet pack src/main.py --distpath ./dist --name Kage
```

#### GitHub Actions での自動ビルド

プロジェクトには`.github/workflows/build_windows.yml`が設定されており、以下の機能を提供：

- プルリクエスト・プッシュ時の自動テスト
- リリースタグ作成時の自動ビルド・デプロイ
- Windows 用実行ファイルの生成

**手動ビルドトリガー**:

1. GitHub リポジトリの "Actions" タブに移動
2. "Build Windows" ワークフローを選択
3. "Run workflow" ボタンをクリック

### セキュリティ考慮事項

#### 開発時の注意点

```bash
# 機密情報の環境変数管理
cp .env.example .env
# .envファイルを編集（Gitにコミットしない）

# pre-commitフックでセキュリティチェック
uv run pre-commit run --all-files
```

### バックアップ・復元

#### データベースバックアップ

```bash
# SQLiteデータベースのバックアップ
cp storage/data/kage.db storage/data/backup_$(date +%Y%m%d).db

# 設定ファイルのバックアップ
tar -czf config_backup.tar.gz .env pyproject.toml alembic.ini
```

---

## ドキュメント更新履歴

- **2025 年 8 月 6 日**: uv の最新情報とプロジェクト構成に基づいて全面改訂
- **uv 0.7.3 対応**: 最新の uv コマンドと機能に対応
- **Flet 0.27.6 対応**: 最新の Flet バージョンの起動方法を反映
- **開発ワークフロー**: VS Code 統合とタスクランナーの説明を追加
