# ブランチ命名規則

最小限で分かりやすく。`fix/内容` みたいな形。

## 基本形

```text
<type>/<slug>
```

`slug` は英小文字 + 数字 + ハイフン。日本語可だがスペースは `-` に。短く。

## type 一覧

| type     | 用途                 |
| -------- | -------------------- |
| feature  | 新機能               |
| fix      | バグ修正             |
| refactor | 挙動変えない整理     |
| perf     | パフォーマンス改善   |
| chore    | 雑タスク / 依存更新 / リリースノートに含めない作業  |
| build    | ビルド/依存/設定変更 |
| ci       | CI 周り              |
| docs     | ドキュメント         |
| test     | テスト追加/調整      |
| revert   | 取り消し用           |
| spike    | 検証用 (短命)        |

## Issue 番号併用 (任意)

```text
<type>/<issue-number>-<slug>
```

例: `fix/123-null-pointer`, `feature/45-task-filter`

## 禁止 / 避ける

- 大文字
- スペース (→ `-`)
- アンダースコア `_`
- 先頭 / 末尾のハイフン
- 100 文字超え
- 意味不明 (`fix/tmp`, `feature/test` など)

## 良い例

```text
fix/textarea-overflow
feature/task-tag-rel
docs/branch-naming
refactor/service-layer-split
perf/query-cache
chore/update-ruff
ci/add-windows-job
```

## 悪い例

```text
Fix/Overflow        # 大文字
fix/テスト 修正      # スペース
feature_task_api    # アンダースコア
fix/tmp             # 意味不明
```

## 運用フロー (推奨)

1. main から作成
2. コミット & PR 作成 (Draft 可)
3. レビュー & squash merge
4. マージ後ローカルとリモートのブランチ削除

## 補足

- spike は成果まとまったら feature / fix に作り直し
- revert/ ブランチは GitHub の "Revert" ボタン利用時にも合わせる
- 迷ったら `fix/明確な短い説明` か `chore/...` に寄せる
