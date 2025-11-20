---
title: Task-Tag コマンド
---

タスクとタグの関連付け管理。タスクへタグを付与 / 解除したり、フィルタ付きで関連一覧を表示できます。

## 主なコマンド

| コマンド例                                          | 説明                           |
| --------------------------------------------------- | ------------------------------ |
| `uv run poe cli task-tag add <TASK_ID> <TAG_ID>`    | タスクへタグを付与             |
| `uv run poe cli task-tag remove <TASK_ID> <TAG_ID>` | タスクから特定タグを解除       |
| `uv run poe cli task-tag list`                      | すべての関連を一覧             |
| `uv run poe cli task-tag list --task <TASK_ID>`     | 特定タスクに紐づくタグ一覧     |
| `uv run poe cli task-tag list --tag <TAG_ID>`       | 特定タグが付与されたタスク一覧 |
| `uv run poe cli task-tag clear-task <TASK_ID>`      | タスクに付与された全タグ解除   |
| `uv run poe cli task-tag clear-tag <TAG_ID>`        | タグが付与された全タスク解除   |
| `uv run poe cli task-tag exists <TASK_ID> <TAG_ID>` | 存在確認 (exit code 0/1)       |

## 例

```bash
# 付与
uv run poe cli task-tag add 11111111-1111-1111-1111-111111111111 22222222-2222-2222-2222-222222222222

# 一覧 (タスクフィルタ)
uv run poe cli task-tag list --task 11111111-1111-1111-1111-111111111111

# 存在確認 (シェル条件分岐に利用)
uv run poe cli task-tag exists 11111111-1111-1111-1111-111111111111 22222222-2222-2222-2222-222222222222 && echo OK
```

## 内部ヘルパー対応表

| ヘルパー           | 説明                 | Service メソッド               |
| ------------------ | -------------------- | ------------------------------ |
| `_create_relation` | 関連作成             | `create_task_tag`              |
| `_delete_relation` | 単一関連削除         | `delete_task_tag`              |
| `_list_all`        | 全関連取得           | `get_all_task_tags`            |
| `_list_by_task`    | タスク ID で絞り込み | `get_task_tags_by_task_id`     |
| `_list_by_tag`     | タグ ID で絞り込み   | `get_task_tags_by_tag_id`      |
| `_get_single`      | 単一取得             | `get_task_tag_by_task_and_tag` |
| `_exists`          | 存在確認             | `check_task_tag_exists`        |
| `_clear_task`      | タスク関連一括削除   | `delete_task_tags_by_task_id`  |
| `_clear_tag`       | タグ関連一括削除     | `delete_task_tags_by_tag_id`   |

## API リファレンス

::: src.cli.commands.task_tag
options:
show_root_heading: false
