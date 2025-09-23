# エラーハンドリング方針 (CLI)

CLI コマンドは `handle_cli_errors` デコレータで一元的に例外を整形表示します。

## ポリシー

| 例外型         | 表示スタイル | 動作                    |
| -------------- | ------------ | ----------------------- |
| `ValueError`   | 黄色 Warning | メッセージのみ表示      |
| `RuntimeError` | 赤 Error     | メッセージのみ表示      |
| その他         | 赤 Panel     | "Unexpected" 見出し表示 |

Traceback はデフォルト非表示 (将来的に `--debug` 追加予定)。内部ログ用途として stderr には traceback を出力しています。

## 実装概要

`cli/utils.py` に以下のデコレータを実装:

- `handle_cli_errors()`: 例外捕捉と Rich Panel による色分け表示
- 既存 `with_spinner`, `elapsed_time` との併用順: `@app.command` → `@handle_cli_errors()` → 関数本体内部で helper 呼び出し

## 適用範囲

`task`, `tag`, `project`, `task-tag`, `memo` 全コマンド関数へ適用済み。

## 今後の拡張候補

- `--debug` / `KAGE_DEBUG=1` で traceback 表示切替
- エラーコードポリシー細分化 (ドメイン例外別 exit code)
- JSON 出力モード時の構造化エラー (`{"error": {"type": ..., "message": ...}}`)
