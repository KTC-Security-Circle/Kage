# Task Quick Actions (`task-qa`)

タスク生成を高速化するための定型アクション群を操作する CLI グループです。

## コマンド一覧

| コマンド   | 説明                                                 |
| ---------- | ---------------------------------------------------- |
| `list`     | 登録済みクイックアクション一覧を表示                 |
| `describe` | 指定キーの詳細 (説明 / プロンプト / タグなど) を表示 |
| `create`   | アクションを実行しタスク生成                         |

## 代表的な利用シナリオ

1. どんなテンプレートがあるか把握したい → `list`
2. 具体的なアクション内容を確認したい → `describe <key>`
3. すぐにタスクを追加したい → `create <key>`

## 例

```bash
# 一覧表示
poe cli task-qa list

# 詳細表示
poe cli task-qa describe daily_reflection

# タスク作成 (INBOX へ追加)
poe cli task-qa create daily_reflection
```

`describe` は Rich Panel で以下を出力します:

- Key
- 説明
- テンプレート本文
- タグ / 付与予定ステータス

`create` は生成されたタスクタイトルを表示します。

## エラーケース

| ケース           | 挙動                                               |
| ---------------- | -------------------------------------------------- |
| 存在しない key   | `ResourceNotFoundError` を捕捉しユーザ向け警告表示 |
| ストレージ不整合 | ログ出力し CLI は失敗コード                        |

---

実装参照: `src/cli/commands/task_qa.py`。
