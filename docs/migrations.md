# マイグレーションの方法

## 基本的なコマンド
```bash

# マイグレーションの適用
# ここでは、最新のマイグレーションを適用するコマンド
# 基本的に最初に行うこと
uv run alembic upgrade head

# マイグレーションのダウングレード
## ここでは、1つ前のバージョンに戻すコマンド
uv run alembic downgrade -1

# マイグレーションの履歴を表示
uv run alembic history

# 特定のバージョンのマイグレーションを適用
## ここでは、特定のバージョンIDを指定してマイグレーションを適用
uv run alembic upgrade <version_id>

# 特定のバージョンにダウングレード
## ここでは、特定のバージョンIDを指定してダウングレード
uv run alembic downgrade <version_id>

# マイグレーションの状態を確認
## ここでは、現在のデータベースの状態を確認するコマンド
uv run alembic current
```

# モデルの追加方法
```python
# src/models/task.py

# モデル(例)
class Project(SQLModel, table=True):
    """プロジェクトモデル

    プロジェクト情報を管理するテーブル。

    Attributes:
        id (int | None): プロジェクトID
        name (str): プロジェクト名
        created_at (datetime): 作成日時
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
```

```python
# src/models/migrations/env.py
from src.models.task import Task, Project # ここでモデルをインポート

# モデルのメタデータをターゲットに設定
target_metadata = [
    Task.metadata,
    Project.metadata, # 他のモデルも必要に応じて追加
]
```
# マイグレーションの作成
```bash
# 新しいマイグレーションを作成
uv run alembic revision --autogenerate -m "add project table"
```