# Proposal: logic 層テストコードの見直しとカバレッジ向上

<!-- OPENSPEC:START -->

## Why

Service 層と Repository 層に未網羅の分岐・例外処理が存在し、現状のカバレッジは 54-78% の範囲に留まっている。
これらは回帰の温床となりやすく、将来の変更時に予期せぬ不具合を見逃すリスクが高い。テストの冗長・重複も散見され、
実行時間や保守性の観点で改善余地があるため、計画的にカバレッジと品質を引き上げる必要がある。

## Summary

logic 配下 (application / services / repositories / infra) のテストコードを整理し、欠落しているエッジケースと例外系を追加して、層ごとのカバレッジを計画的に引き上げる。テストは既存のフィクスチャとインメモリ DB を活用しつつ、過度なモックを避けてビジネスルールの回帰を確実に捕捉する。

## Goals

- Service 層と Repository 層の分岐・例外を重点的にテスト追加
- 現行テストの冗長さ/重複の削減と命名・レイアウトの調整
- カバレッジの閾値を段階設定し、失敗時は明確に可視化

## Non-goals

- 本提案ではアプリの新機能追加や API 仕様変更は対象外
- 既存プロダクションコードの大規模リファクタリングは対象外 (テストから発見された明確な欠陥の修正は別 PR/提案で対応)

## Scope

- 対象: `src/logic/**` と `tests/logic/**`
- 含む: Service/Repository/Application/Infra(Unit of Work, Factory) のユニット/軽い統合テスト
- 含まない: UI 層、エージェント層のテスト

## What

- 未到達分岐・例外のテスト追加 (NotFound、空集合、with_details 分岐 等)
- UnitOfWork/Factory のロールバック/ライフサイクルのエッジ検証
- 冗長テストの統合/命名統一と軽量化
- カバレッジ閾値の段階引き上げ

## How

- 既存の conftest/fixtures/helpers を流用し、DB はインメモリを基本とする
- pytest 参数化でパス網羅を効率化、外部依存は最小限のモックに留める
- poe test-cov による term-missing 出力で穴を特定し、差分追加を繰り返す

## Success Criteria

- pytest-cov による計測で閾値達成 (詳細は specs を参照)
- 代表的な失敗系 (NotFound、バリデーション、分岐未到達) がテストで網羅
- テスト時間は現状比で大きく悪化しない (目安 +20% 以内)

## Impact

- CI での失敗検知が早期化される
- 既存の潜在不具合が浮上する可能性はあるが、品質向上に資する
- 実行時間は最大 +20% 程度の増加を見込む

## Risks & Mitigations

- 新規テストにより既存の潜在不具合が顕在化する可能性: テストで検出された欠陥は別 PR/提案に切り出して段階的に修正
- カバレッジ閾値による CI 失敗リスク: 段階的な閾値引き上げと、対象スコープの限定でコントロール

## References

- tests/logic/COVERAGE_REPORT.md (現状: 総合 80%、Service 54-65%、Repository 71-78%)
- pyproject.toml (pytest/pytest-cov 設定、poe task)

<!-- OPENSPEC:END -->
