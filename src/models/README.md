# 初回マイグレーション作成
uv run alembic revision --autogenerate -m "Initial migration"

# マイグレーション適用
uv run alembic upgrade head

# モデル変更後のマイグレーション作成
uv run alembic revision --autogenerate -m "Add new field"