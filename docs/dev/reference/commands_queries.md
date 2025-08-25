# コマンド / クエリ一覧

アプリケーションサービス層に処理を依頼するための 2 種類の DTO (Command / Query) をまとめて参照できるページです。UI や Agent からドメイン操作を行う際に、状態を変更するか（Command）、取得するか（Query）で使い分けます。

| 区分    | 目的                                    | 副作用 | 命名例                | 代表メソッド/変換                          |
| ------- | --------------------------------------- | ------ | --------------------- | ------------------------------------------ |
| Command | 状態変更(作成/更新/削除/ステータス変更) | あり   | CreateTaskCommand     | to_task_create(), to_project_update() など |
| Query   | 状態取得(検索/一覧/件数/存在確認)       | なし   | GetTasksByStatusQuery | (変換不要: 条件値のみ)                     |

## Command オブジェクトについて

書き込み系ユースケース（状態変更）を依頼するための不変 DTO です。呼び出し側は必要最小限の入力をまとめ、Application Service に渡します。

設計指針:

- 1 コマンド = 1 ユースケース (副作用を伴う操作)
- dataclass により軽量でテスト容易
- `to_xxx_create` / `to_xxx_update` などでモデルへ変換
- Validation は上位 (UI/Service) で実施し、DTO 自体はデータキャリア

### 利用例 (タスク作成)

```python
from logic.commands.task_commands import CreateTaskCommand
from logic.application_services.task_application_service import TaskApplicationService

cmd = CreateTaskCommand(title="調査", description="仕様確認")
service = TaskApplicationService(...)
service.create_task(cmd)
```

## Query オブジェクトについて

読み取り系ユースケース（状態取得）を依頼するための DTO です。フィルタ条件をカプセル化しサービス層に渡します。

設計指針:

- 1 クエリ = 1 読み取りユースケース (副作用なし)
- dataclass によりシンプル
- 条件/識別子のみを保持しロジックを持たない
- 複雑化する場合は新たな専用クエリを追加し責務分離

### 利用例 (ステータス別タスク取得)

```python
from logic.queries.task_queries import GetTasksByStatusQuery
from logic.application_services.task_application_service import TaskApplicationService
from models import TaskStatus

q = GetTasksByStatusQuery(status=TaskStatus.INBOX)
service = TaskApplicationService(...)
tasks = service.get_tasks_by_status(q)
```

---

## コマンド API リファレンス

### タスク関連コマンド

::: src.logic.commands.task_commands

### プロジェクト関連コマンド

::: src.logic.commands.project_commands

### タグ関連コマンド

::: src.logic.commands.tag_commands

### タスクタグ関連コマンド

::: src.logic.commands.task_tag_commands

---

## クエリ API リファレンス

### プロジェクト関連クエリ

::: src.logic.queries.project_queries

### タグ関連クエリ

::: src.logic.queries.tag_queries

### タスク関連クエリ

::: src.logic.queries.task_queries

### タスクタグ関連クエリ

::: src.logic.queries.task_tag_queries
