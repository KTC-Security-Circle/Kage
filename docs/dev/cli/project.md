# Project コマンド

プロジェクト管理操作。

## 一覧

```bash
poe cli project list
```

## 作成

```bash
poe cli project create --title "Refactor" --desc "Improve CLI layer" --status active
```

## 検索

```bash
poe cli project search refactor
```

## 取得

```bash
poe cli project get <PROJECT_ID>
```

## 更新

```bash
poe cli project update <PROJECT_ID> --title "Refactor v2" --desc "More improvements" --status on_hold
```

## 削除

```bash
poe cli project delete <PROJECT_ID>
poe cli project delete <PROJECT_ID> --force
```

## 内部ヘルパー対応表

| ヘルパー            | 説明         | Service メソッド           |
| ------------------- | ------------ | -------------------------- |
| `_get_all_projects` | 全件取得     | `get_all_projects`         |
| `_create_project`   | 作成         | `create_project`           |
| `_get_project`      | 単体取得     | `get_project_by_id`        |
| `_search_projects`  | タイトル検索 | `search_projects_by_title` |
| `_update_project`   | 更新         | `update_project`           |
| `_delete_project`   | 削除         | `delete_project`           |
