マイグレーション適応
```bash
cd src/models
uv run alembic upgrade head
```


# メモ

## 初回マイグレーション作成
uv run alembic revision --autogenerate -m "Initial migration"

## マイグレーション適用
uv run alembic upgrade head

## モデル変更後のマイグレーション作成
uv run alembic revision --autogenerate -m "Add new field"
