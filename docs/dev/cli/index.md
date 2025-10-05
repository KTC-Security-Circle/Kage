# CLI クイックリファレンス

Kage の CLI は Typer ベースで `poe cli <group> <command>` 形式で利用します。以下は主要なサブコマンドの概要です。

## グループ一覧

| グループ   | 目的             | 主な操作                                                 |
| ---------- | ---------------- | -------------------------------------------------------- |
| `task`     | タスク管理       | 作成 / 一覧 / 取得 / 更新 / ステータス変更 / 削除 / 統計 |
| `task-tag` | タスクとタグ関連 | 付与 / 解除 / 一覧 / 存在確認 / 一括解除                 |
| `memo`     | メモ管理         | 作成 / 更新 / 削除 / 取得 / 一覧 / 検索                  |
| `tag`      | タグ管理         | 作成 / 一覧 / 取得 / 検索 / 更新 / 削除                  |
| `project`  | プロジェクト管理 | 作成 / 一覧 / 取得 / 検索 / 更新 / 削除                  |

## よく使う例

```bash
# タスク一覧 (INBOX)
poe cli task list

# すべてのタスク一覧
poe cli task list --all

# タスク作成
poe cli task create --title "Write docs" --desc "CLI pages" --due 2025-09-30

# プロジェクト検索
poe cli project search refactor

# タグ検索
poe cli tag search urgent
```

詳細: [Task コマンド](task.md) / [Task-Tag コマンド](task_tag.md) / [Memo コマンド](memo.md) / [Tag コマンド](tag.md) / [Project コマンド](project.md) / [エラーハンドリング](error_handling.md) / [開発者向け](dev.md)
