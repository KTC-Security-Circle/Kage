---
title: Memo コマンド
---

タスクに紐づくメモの CRUD / 検索を提供します。内容を省略すると対話入力になります。

## 主なコマンド

| コマンド例                                       | 説明                      |
| ------------------------------------------------ | ------------------------- |
| `poe cli memo create --task <TASK_ID> -c "text"` | メモ作成                  |
| `poe cli memo update <MEMO_ID> -c "new content"` | メモ内容更新              |
| `poe cli memo delete <MEMO_ID>`                  | メモ削除 (確認プロンプト) |
| `poe cli memo delete <MEMO_ID> --force`          | メモ削除 (確認なし)       |
| `poe cli memo get <MEMO_ID>`                     | 単一取得                  |
| `poe cli memo list`                              | 全件一覧                  |
| `poe cli memo list --task <TASK_ID>`             | タスク ID フィルタ        |
| `poe cli memo search <QUERY>`                    | 部分一致検索              |

## 例

```bash
# 作成 (内容は対話入力)
poe cli memo create --task 11111111-1111-1111-1111-111111111111

# 更新 (内容指定)
poe cli memo update 33333333-3333-3333-3333-333333333333 -c "Fix wording"

# 検索
poe cli memo search meeting
```

## 内部ヘルパー対応表

| ヘルパー        | 説明         | Service メソッド       |
| --------------- | ------------ | ---------------------- |
| `_create_memo`  | 作成         | `create_memo`          |
| `_update_memo`  | 更新         | `update_memo`          |
| `_delete_memo`  | 削除         | `delete_memo`          |
| `_get_memo`     | 単一取得     | `get_memo_by_id`       |
| `_list_all`     | 全件一覧     | `get_all_memos`        |
| `_list_by_task` | タスク別取得 | `get_memos_by_task_id` |
| `_search_memos` | 部分一致検索 | `search_memos`         |

## API リファレンス

::: src.cli.commands.memo
    options:
        show_root_heading: false
