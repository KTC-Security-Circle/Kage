# home-one-liner-refresh Specification

## Purpose

TBD - created by archiving change update-oneliner-hourly-refresh. Update Purpose after archive.

## Requirements

### Requirement: Hourly One-Liner Refresh Budget

Home 画面で利用する一言メッセージ生成（`OneLinerApplicationService.generate_one_liner()` のクエリ省略モード）は、LLM エージェントを 1 時間に 1 回までに抑制し、同一プロセス内では前回のメッセージと生成時刻をキャッシュして返さなければならない (MUST)。TTL は 60 分とし、期限切れ後の最初の呼び出しのみ新たにコンテキストを収集してエージェントを呼び出す (MUST)。明示クエリが指定された場合はキャッシュを参照せず、即座にエージェントへ委譲する (MUST)。

#### Scenario: Cached Greeter Within TTL

- **WHEN** Home 画面が 30 分以内に 2 回 `generate_one_liner()` を呼び出す
- **THEN** 最初の呼び出しのみエージェントを起動し、2 回目はキャッシュを返してレスポンスが即時に返る

#### Scenario: Refresh After TTL Expiration

- **WHEN** 前回生成から 60 分以上経過した状態で `generate_one_liner()` が呼び出される
- **THEN** サービスはキャッシュを破棄し、最新のタスク状況を取り込み直してエージェントを再実行する

#### Scenario: Explicit Query Bypasses Cache

- **WHEN** `OneLinerState` クエリを明示的に渡して `generate_one_liner(query)` を呼ぶ
- **THEN** キャッシュ状態に関わらずエージェントを起動し、呼び出しごとに最新の応答を返す
