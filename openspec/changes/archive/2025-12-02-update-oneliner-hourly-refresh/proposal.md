## Why

Home 画面を開くたびに `OneLinerApplicationService.generate_one_liner()` が LLM を起動しており、ページ遷移のたびに推論コストと待ち時間が発生している。意図としては 1 時間に 1 回だけ AI メッセージを更新できれば十分なので、生成頻度を制御したい。

## What Changes

- クエリ省略モード（Home 画面が利用）では 1 時間以内の連続呼び出しをキャッシュで返し、`OneLinerAgent` 実行を抑制する。
- TTL が切れた場合・明示クエリが渡された場合には従来どおり LLM を実行する。
- ロジック層に留めた変更に合わせ、`OneLinerApplicationService` とそのユニットテストのみを更新する。

## Impact

- Affected specs: `home-one-liner-refresh`
- Affected code: `src/logic/application/one_liner_application_service.py`, `tests/logic/application/test_one_liner_application_service.py`
