# Task コマンド

タスク管理操作。サービス呼び出しは内部ヘルパー (スピナー + 計測) 経由。

## 一覧表示

```bash
poe cli task list --status inbox
poe cli task list --all            # 全ステータス
```

## 作成

```bash
poe cli task create --title "Write docs" --desc "Add CLI docs" --due 2025-09-30 --status inbox
```

対話モード (オプション省略時) も可。

## 取得

```bash
poe cli task get <TASK_ID>
```

## 更新

```bash
# すべて任意。未指定は対話 or 現在値を利用
poe cli task update <TASK_ID> --title "New title" --desc "New desc" --status next_action --due 2025-10-01
```

## ステータス変更ショート

```bash
poe cli task status <TASK_ID> done
```

## 削除

```bash
poe cli task delete <TASK_ID>
poe cli task delete <TASK_ID> --force  # 確認なし
```

## 内部ヘルパー対応表

| ヘルパー          | 説明                   | Service メソッド               |
| ----------------- | ---------------------- | ------------------------------ |
| `_load_tasks`     | ステータス別取得       | `get_tasks_by_status`          |
| `_list_all_tasks` | 全ステータス dict 取得 | `get_all_tasks_by_status_dict` |
| `_create_task`    | 作成                   | `create_task`                  |
| `_get_task`       | 単体取得               | `get_task_by_id`               |
| `_update_task`    | 更新                   | `update_task`                  |
| `_change_status`  | ステータス変更         | `update_task`                  |
| `_delete_task`    | 削除                   | `delete_task`                  |

## 統計表示 (stats)

タスク件数の簡易統計を表示。

```bash
poe cli task stats                # today/completed/overdue を表示
poe cli task stats --no-overdue   # overdue を省略
```

メトリクス:

- Today: 期限日が今日のタスク件数
- Completed: 完了済件数
- Overdue: 期限超過 (未完了) 件数

内部では 3 つのサービスメソッドを個別に計測し、最大 elapsed を代表値として表示。

## API リファレンス

::: src.cli.commands.task
    options:
        show_root_heading: false
