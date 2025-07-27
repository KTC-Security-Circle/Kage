# マイグレーションの方法

## 基本的なコマンド

```bash
# 最初にmigrationsという名前で作成
alembic init migrations

# 変更の検出とマイグレーションファイルの生成
# ここでは、"create tables"というメッセージを付けてマイグレーションを作成
# これにより、現在のデータベースの状態に基づいてマイグレーションが生成されます
# 生成されたマイグレーションファイルは、migrations/versionsディレクトリに保存されます
# これにより、データベースのスキーマを管理しやすくなります
alembic revision --autogenerate -m "create tables"

# マイグレーションの適用
alembic upgrade head

# マイグレーションのダウングレード
## ここでは、1つ前のバージョンに戻すコマンド
alembic downgrade -1

# マイグレーションの履歴を表示
alembic history

# 特定のバージョンのマイグレーションを適用
## ここでは、特定のバージョンIDを指定してマイグレーションを適用
alembic upgrade <version_id>

# 特定のバージョンにダウングレード
## ここでは、特定のバージョンIDを指定してダウングレード
alembic downgrade <version_id>

# マイグレーションの状態を確認
## ここでは、現在のデータベースの状態を確認するコマンド
alembic current
```
