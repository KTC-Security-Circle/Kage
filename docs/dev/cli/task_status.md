# Task Status / Board (`task-status`)

タスクのステータス・ボード列構成を確認するための CLI グループです。

## コマンド

| コマンド   | 説明                                                   |
| ---------- | ------------------------------------------------------ |
| `displays` | 表示用ステータスセット (集計やビューで利用) を一覧表示 |
| `board`    | カンバン列 (ステータス配列) を表示                     |

## 例

```bash
poe cli task-status displays
poe cli task-status board
```

### `displays` 出力

Rich Table で 下記のような集合を表示 (例):

```text
INBOX / TODO / DOING / WAITING / DONE / ARCHIVED
FOCUS / BACKLOG / COMPLETED_TODAY
```

### `board` 出力

ボード列となるステータス配列を左 → 右の順序で表示します。

## ユースケース

- 新しいビューを実装する際に利用するステータス集合を把握
- 外部連携 (Notion 等) のカラムマッピング検討

---

実装参照: `src/cli/commands/task_status.py`。
