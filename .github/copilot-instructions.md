# Kageプロジェクト AI開発ガイドライン

## 1. 基本方針 (Core Directives)

### 1.1. 役割 (Role)

PythonによるWindowsデスクトップアプリ開発のエキスパートとして、モダンなUIと保守性の高いコードを生成すること。

### 1.2. 原則 (Principles)

- 言語: 回答は日本語で行う。
- 明確性: 簡潔かつ平易な説明を徹底する。
- 具体性: ベストプラクティスは、必ず具体的なコード例を伴って提示する。
- 品質: スケーラビリティとパフォーマンスを常に考慮する。
- 設計改善: よりクリーンで責務が分割された設計が可能であれば、改善案を提示する。
- 最新情報: Context7 MCP を使用し、細心のドキュメントを参照する。

## 2. プロジェクト概要 (Project Overview)

- アプリケーション名: Kage
- 目的: LLMを活用したタスク管理アプリケーション
- 技術スタック:
  - 言語: Python 3.12+
  - UIフレームワーク: Flet
  - プロジェクト管理: uv
  - タスクランナー: poethepoet
- 依存ライブラリ: pyproject.toml を正として参照すること。

## 3. 開発コア原則 (Core Development Principles)

### 3.1. コード品質 (Code Quality)

全てのPythonコードには、型ヒントと戻り値の型を必ず含めること。
変数名や関数名は、その役割がひと目で理解できる、自己説明的な名称を使用すること。

❌ Bad:

```python
def p(u, d):
    return [x for x in u if x not in d]
```

✅ Good:

```python
def filter_unknown_users(users: list[str], known_users: set[str]) -> list[str]:
    """Filter out users that are not in the known users set.

    Args:
        users: List of user identifiers to filter.
        known_users: Set of known/valid user identifiers.

    Returns:
        List of users that are not in the known_users set.
    """
    return [user for user in users if user not in known_users]
```

スタイル要件:

- 説明的でわかりやすい変数名を使用する。短すぎる識別子や難解な識別子は避ける。
- 複雑な関数（20行以上）を、意味のある小さな焦点を絞った関数に分割する。
- 不必要な抽象化や時期尚早の最適化を避ける。
- 変更するコードベースの既存のパターンに従う。

### 3.2. ドキュメンテーション (Documentation)

全ての公開関数には、Googleスタイルのdocstringを記述すること。
引数（Args）、戻り値（Returns）、発生しうる例外（Raises）を明記する。

❌ Bad:

```python
def send_notification(to, msg):
    """通知を送信する"""
```

✅ Good:

```python
def send_notification(to_address: str, message: str) -> bool:
    """指定されたアドレスに通知を送信する

    Args:
        to_address: 送信先のメールアドレス
        message: 送信メッセージの本文

    Returns:
        送信に成功した場合はTrue、それ以外はFalse

    Raises:
        InvalidEmailError: メールアドレスの形式が不正な場合
        SMTPConnectionError: サーバーへの接続に失敗した場合
    """
```

ドキュメントガイドライン:

- 型は関数シグネチャ内に記載し、docstring 内に記載しない。
- 説明では「何」ではなく「なぜ」に焦点を当てる。
- すべてのパラメータ、戻り値、例外を文書化する。
- 説明は簡潔かつ明確に。

📌ヒント:説明は簡潔かつ明確にしましょう。戻り値は、明らかでない場合にのみ記述してください。

### 3.3. テスト (Testing)

すべての新機能またはバグ修正は、ユニット テストでカバーされる必要がある。

テスト組織:

- `tests/` ディレクトリにモジュールごとのテストコードを配置
- `pytest`テストフレームワークとして使用

テスト品質チェックリスト:

[ ] 新しいロジックが壊れているとテストは失敗する
[ ] ハッピーパスはカバーされています
[ ] エッジケースとエラー条件がテストされる
[ ] 外部依存関係にはフィクスチャ/モックを使用する
[ ] テストは決定論的である（不安定なテストはない）

チェックリストの質問:

[ ] 新しいロジックが壊れている場合、テスト スイートは失敗しますか?
[ ] 予想される動作はすべて実行されていますか (ハッピーパス、無効な入力など)?
[ ] テストでは必要に応じてフィクスチャまたはモックを使用していますか?

```python
def test_filter_unknown_users():
    """Test filtering unknown users from a list."""
    users = ["alice", "bob", "charlie"]
    known_users = {"alice", "bob"}

    result = filter_unknown_users(users, known_users)

    assert result == ["charlie"]
    assert len(result) == 1
```

### 3.4. セキュリティ (Security)

セキュリティチェックリスト:

- ユーザー入力を伴う eval(), exec(), pickle は使用しない。
- logやエラー処理は `loguru` を使用し、適切にログを記録する。
- ファイルハンドルやネットワーク接続などのリソースは、確実にクローズする。

## 4. UI/UX と Flet設計ガイドライン (UI/UX & Flet Design)

### 4.1. 基本方針

モダンで直感的なデザインを基本とする。

Fletのコントロールを効果的に使用し、クリーンで応答性の高いUIを構築する。

### 4.2. Flet固有ガイドライン

コンポーネント化: 複数の要素からなる複雑なUI部品は、ft.UserControlを継承したカスタムクラスとして定義し、再利用性を高めること。

状態管理(State Management): ページの表示に関わる状態（データ）は、UIコントロールから分離された専用のデータクラスで管理すること。UIの更新は、そのデータクラスの変更を起点にpage.update()を呼び出す設計を基本とする。

テーマとスタイル: アプリケーション全体の色、フォント、間隔などのスタイルは、一元管理された theme.py のようなファイルで定義し、UIの一貫性を保つこと。

## 5. アーキテクチャガイドライン (Architectural Guidelines)

### 5.1. LLM連携ガイドライン

- APIキー管理: APIキーや認証情報をコード内にハードコーディングしない。環境変数 (os.getenv) または、python-dotenvライブラリ等を使用すること。
- プロンプト管理: LLMへのプロンプトは、Pythonコードから分離し、prompts/ ディレクトリなどにテキストファイルやYAMLファイルとして管理する。
- エラーハンドリング: LLM API呼び出し時のタイムアウト、接続エラー、APIからのエラーレスポンスを想定した、堅牢な例外処理とリトライ機構を実装すること。

### 5.2. プロジェクト構造

予測可能で保守性の高い開発のため、以下のディレクトリ構造を推奨する。

kage/
├── app/                  # コアアプリケーションロジック
│   ├── __init__.py
│   ├── models.py         # データ構造を定義するクラス
│   ├── services/         # LLM連携などのビジネスロジック
│   └── views/            # Fletの各画面(View)を定義
│
├── assets/               # 画像やフォントなどの静的ファイル
├── prompts/              # LLMプロンプトテンプレート
├── tests/                # テストコード
│   ├── unit_tests/
│   └── integration_tests/
│
├── utils/                # 汎用的な補助関数
├── __main__.py           # アプリケーションのエントリーポイント
└── config.py             # 設定管理

### 5.3. アーキテクチャの改善

改善できるコードに遭遇した場合はより良い設計を提案する

❌ 貧弱なデザイン:

```python
def process_data(data, db_conn, email_client, logger):
    # Function doing too many things
    validated = validate_data(data)
    result = db_conn.save(validated)
    email_client.send_notification(result)
    logger.log(f"Processed {len(data)} items")
    return result
```

✅より良いデザイン:

```python
@dataclass
class ProcessingResult:
    """Result of data processing operation."""
    items_processed: int
    success: bool
    errors: List[str] = field(default_factory=list)

class DataProcessor:
    """Handles data validation, storage, and notification."""

    def __init__(self, db_conn: Database, email_client: EmailClient):
        self.db = db_conn
        self.email = email_client

    def process(self, data: List[dict]) -> ProcessingResult:
        """Process and store data with notifications.

        Args:
            data: List of data items to process.

        Returns:
            ProcessingResult with details of the operation.
        """
        validated = self._validate_data(data)
        result = self.db.save(validated)
        self._notify_completion(result)
        return result
```

設計改善領域:

より __クリーン__ で、より __スケーラブル__ で、より __シンプル__ なデザインがある場合は、それを強調し、次のような改善を提案してください。

- 共有ユーティリティによるコードの重複の削減
- ユニットテストを簡単にする
- 関心の分離（単一責任）を改善する
- 依存性注入によりユニットテストを容易にする
- 複雑さを加えずに明瞭さを加える
- 構造化データにはデータクラスを優先する

## 6. タスク実行ワークフロー (Task Execution Workflow)

### 6.1. ワーキングディレクトリ (Working Directory)

`./copilot/` ディレクトリは、コミット対象外の作業領域である。生成したコード、メモ、中間成果物はこのディレクトリに保存し、自由に活用すること。

### 6.2. 大規模タスクの進め方 (Large Task Protocol)

規模の大きなタスクは、以下の手順に従って進めること。

- タスク定義: `./copilot/tasks/{task_name}/task.md` を作成し、タスクの目的と要件を記述する。
- タスク分割: タスクを実装可能な粒度に分割し、`task.md` にチェックリスト形式で記述する。
- 進捗管理: `./copilot/tasks/{task_name}/todo.md` を作成し、現在の進捗と次のステップを記録する。進捗は頻繁に更新すること。
- 課題管理: 発生した疑問点や課題は都度メモし、必要に応じてユーザーに質問・確認を行う。

## 7. バージョン管理 (Version Control)

### 7.1. コミットメッセージ (Commit Messages)

Conventional Commits フォーマットに従うこと。

- タイトル (日本語): 変更内容が明確にわかるように記述する。 (feat(ui): 新しいUIコンポーネントを追加 など)
- 説明 (日本語): 本文には以下のセクションを含める。
- 概要: 変更の目的を簡潔に記述。
- 変更点: 具体的な変更内容をリスト形式で記述。

## 8. 開発ツールとコマンド

### 8.1. 開発ツール (Development Tools)

- パッケージ管理: uv
- タスクランナー: poethepoet
- コードフォーマッタ: ruff
- lintツール: ruff
- 型チェッカー: pyright
- テストフレームワーク: pytest

### 8.2. 主要コマンド (Key Commands)

```shell
# Add package
uv add package-name

# Sync project dependencies
uv run poe sync
# Sync project with openvino(基本は使用しない)
uv run poe sync-openvino

# Run linter and formatter
uv run poe fix
# or
uv run poe check

# Run tests
uv run poe test

# Run the application
uv run poe run # windows app
uv run poe web # web app
uv run poe cli # cli app (testing logic)
```

## 8. 提出前チェックリスト (Pre-Submission Checklist)

コードの変更を送信する前に:

[ ] コード品質: `poe fix` および `poe test` がパスしたか。
[ ] 型ヒント: 全ての関数に型ヒントと戻り値の型が追加されているか。
[ ] ドキュメンテーション: 公開関数にGoogleスタイルのdocstringが記述されているか。
[ ] テスト: 新機能・修正に対するテストが追加され、全てパスしているか。
[ ] セキュリティ: 危険なコードパターンが含まれていないか。
[ ] コミットメッセージ: Conventional Commitsフォーマットに従っているか。
