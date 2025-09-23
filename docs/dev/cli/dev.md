# CLI 開発者向けガイド

内部構造と拡張規約を示します。

## アーキテクチャ層

```text
Typer Command -> Decorated Helper (_create_*, _get_* ...) -> Application Service -> Repository/DB
```

## デコレータ

| デコレータ               | 役割               | 戻り値構造                                       |
| ------------------------ | ------------------ | ------------------------------------------------ |
| `@with_spinner(message)` | 実行中スピナー表示 | 元関数の戻り値をそのまま通過                     |
| `@elapsed_time()`        | 実行時間計測       | Namespace(result=<元戻り値>, elapsed=<float 秒>) |

両方適用時は `elapsed_time` が外側にある実装（計測範囲=スピナー含む）。

## ヘルパー関数規約

1. 1 ヘルパー = 1 サービスメソッド呼び出し (YAGNI)
2. 例外処理はサービス層で行い CLI はユーザー向け表示に集中
3. 戻り値をそのまま返しプレゼンテーション変換はコマンド関数側
4. 取得系で存在しない場合は `None` を `.result` に格納 (テーブル出力前に判定)

## 新規コマンド追加手順

1. Service / Command / Query を先に実装
2. `src/cli/commands/<entity>.py` にヘルパー `_do_something` を追加
3. Typer の `@app.command` で CLI 関数実装
4. 出力: テーブル or シンプルな `console.print`
5. ドキュメント: 本ディレクトリに `<entity>.md` へ使用例追記

## 推奨テーブル出力パターン

```python
from rich.table import Table

table = Table(title="Example", caption=f"Elapsed: {result.elapsed:.2f}s")
# カラム定義 -> 行追加 -> console.print(table)
```

## テスト戦略 (将来)

| レベル      | 対象           | 手法                                                  |
| ----------- | -------------- | ----------------------------------------------------- |
| unit        | ヘルパー       | サービスをモックし戻り値と spinner/elapsed 動作を確認 |
| integration | CLI コマンド   | `typer.testing.CliRunner` を利用                      |
| e2e         | 実 DB (sqlite) | 事前にテンポラリ DB をセットアップ                    |

## 追加検討事項

- 共通テーブルビルダーの導入
- 非同期化 (async Typer) 検証
- JSON 出力モード (`--json`) の追加

---

以上。
