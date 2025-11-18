# Tag コマンド

タグ管理操作。

## 一覧

```bash
uv run poe cli tag list
```

## 作成

```bash
uv run poe cli tag create --name "#urgent"
```

## 検索

```bash
uv run poe cli tag search urgent
```

## 取得

```bash
uv run poe cli tag get <TAG_ID>
```

## 更新

```bash
uv run poe cli tag update <TAG_ID> --name "#important"
```

## 削除

```bash
uv run poe cli tag delete <TAG_ID>
uv run poe cli tag delete <TAG_ID> --force
```

## 内部ヘルパー対応表

| ヘルパー        | 説明             | Service メソッド      |
| --------------- | ---------------- | --------------------- |
| `_get_all_tags` | 全件取得         | `get_all_tags`        |
| `_create_tag`   | 作成             | `create_tag`          |
| `_search_tags`  | 名前部分一致検索 | `search_tags_by_name` |
| `_get_tag`      | 単体取得         | `get_tag_by_id`       |
| `_update_tag`   | 更新             | `update_tag`          |
| `_delete_tag`   | 削除             | `delete_tag`          |

## API リファレンス

::: src.cli.commands.tag
options:
show_root_heading: false
