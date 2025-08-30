# 設定・環境変数ガイド

本ドキュメントでは Kage における設定管理と環境変数の仕組み、および拡張方法について説明します。

## 概要

Kage では以下の 3 レイヤで設定値を統合し、優先順位を付けて解決します。

1. 実行時環境変数 (`os.environ`) - 最優先（CI や一時上書きに使用）
2. パース済み `.env` / 既定値 (`EnvSettings` Pydantic モデル)
3. 永続 YAML 設定ファイル (`config.yaml`) - ユーザー編集用の保存層

```text
┌────────────────────┐  ← 1. Runtime Env (os.environ)
│ DATABASE_URL=...    │  # その場で上書き
└──────────┬─────────┘
           ▼ マージ
┌────────────────────┐  ← 2. EnvSettings (.env + 型変換)
│ OPENAI_API_KEY=...  │
└──────────┬─────────┘
           ▼ フォールバック
┌────────────────────┐  ← 3. config.yaml (ruamel.yaml, コメント保持)
│ database:
│   url: sqlite:///... │
└────────────────────┘
```

## 目的

- コメント保持可能な YAML でユーザー設定を永続化
- 型安全 (Pydantic v2) + 変更容易な編集レイヤ
- 環境変数を一元管理し、欠落/未設定を検出
- 実行時の即時上書き（テスト・CI・一時カスタム）

## 主要コンポーネント

| コンポーネント          | 役割                                                 |
| ----------------------- | ---------------------------------------------------- |
| `EnvSettings`           | `.env` 読込と型付きアクセス、未設定警告              |
| `ENV_VARS` (レジストリ) | 利用する環境変数メタ定義（説明/種類/必須）           |
| `ConfigManager`         | YAML 読込/保存、編集トランザクション、統合解決       |
| `edit()` コンテキスト   | 不変モデルを編集可能モデルに一時変換し YAML へ永続化 |

## 環境変数レジストリ

`src/settings/models.py` 内 `ENV_VARS` に `EnvVarDef` のリストとして定義します。

```python
EnvVarDef(name="OPENAI_API_KEY", category="ai", required=False, description="OpenAI API キー")
```

追加手順:

1. `ENV_VARS` に `EnvVarDef` を追加
2. `EnvSettings` にフィールドを型付きで追加（必要なら）
3. ドキュメント更新（本ファイル）

`init_environment()` 実行時の挙動:

- `.env` が無ければテンプレ生成（コメント付き）
- レジストリにあるが .env に欠けているキーを追記
- 必須(required=True) かつ未設定値をログ警告

### 定義一覧 (自動生成)

<!-- BEGIN:ENV_VARS_TABLE -->

| キー | 型 | カテゴリ | デフォルト | コメント |
|---|---|---|---|---|
| FLET_SECRET_KEY | str | flet |  |  |
| GOOGLE_API_KEY | str | ai |  |  |
| LANGSMITH_API_KEY | str | ai |  |  |
| LANGSMITH_TRACING | bool | ai | false | false/true |
| KAGE_USE_LLM_ONE_LINER | bool | ai | false | false/true |
| DATABASE_URL | str | db |  |  |

<!-- END:ENV_VARS_TABLE -->

## 設定値の解決優先順位

`ConfigManager.database_url` などのプロパティでは以下の順で解決:

1. `os.environ.get("DATABASE_URL")`
2. `EnvSettings.get().database_url`（`.env` 由来の型済値）
3. YAML (`config.yaml`) 内の保存値

テストで monkeypatch した環境変数も即時反映されます（`EnvSettings` をキャッシュしない設計）。

## 編集フロー

ランタイム利用は不変 (frozen) Pydantic モデル。編集時は一時的に「編集用モデル」へ変換し、コンテキスト終了で差分を YAML に保存します。

```python
from settings.manager import config_manager

with config_manager.edit() as cfg:
    cfg.app.theme = "dark"
    cfg.database.url = "postgresql+psycopg://user:pass@host/db"
# ← ここで自動保存 & 不変モデルへ戻る
```

### トランザクション特性

- コンテキスト内例外発生時は保存されません
- ネスト編集は最初のコンテキストに集約（深さカウント）
- 差分計算で最小限フィールドを書換

## YAML 永続化

- ライブラリ: `ruamel.yaml`（コメント保持）
- パス: `CONFIG_PATH` (`src/config.py`)
- 未存在時はデフォルト設定で生成

### 生成される初期 config.yaml (抜粋 / 自動生成)

<!-- BEGIN:DEFAULT_CONFIG_YAML -->

```yaml
window:
  size:
    - 1280
    - 720
  position:
    - 100
    - 100
user:
  last_login_user:
  theme: light
database:
  url: sqlite:///storage/data/tasks.db
```

<!-- END:DEFAULT_CONFIG_YAML -->

## よくある追加シナリオ

| シナリオ                  | 手順概要                                             |
| ------------------------- | ---------------------------------------------------- |
| OpenAI API キー追加       | `.env` に値を設定（`OPENAI_API_KEY=sk-...`）         |
| DB 接続を Postgres に切替 | `DATABASE_URL` を環境変数または `.env` で設定        |
| UI テーマ変更             | `with config_manager.edit(): cfg.app.theme = "dark"` |
| 新しい環境変数            | `ENV_VARS` + `EnvSettings` フィールド追加 + doc 追記 |

## テスト戦略概要

- `.env` の欠落キー補完: `init_environment` テスト
- 優先順位: monkeypatch で `os.environ` を上書き → 即時反映検証
- 編集コンテキスト: before/after を比較し immutability を確認
- 空文字ブール → None 変換: バリデータテスト

## ベストプラクティス

- 一時的な上書きは環境変数で行い、永続変更は編集コンテキストで行う
- 必須キーは CI で空チェック（将来的に追加予定）
- 直接 `os.getenv` を使用せず `ConfigManager`/`EnvSettings` 経由に統一

## 今後の改善候補

- `EnvSettings.reload()` の追加（明示再読込）
- `.env.example` の自動同期生成
- 設定 UI (Flet) の提供
- 未使用設定検出スクリプト

---

最終更新: 2025-08-31
