# Proposal: Migrate Projects View to Logic Layer (UI unchanged)

## Change ID

migrate-projects-to-logic-layer

## Summary

Projects 画面を、既存の memos 画面と同等の「View → Controller → ApplicationService(Port)」構成へ移行する。Repository/Query への直接依存を廃し、ProjectApplicationService 経由のユースケース実行に統一する。UI は変更せず（コンポーネント/API/VM 形状は維持）、内部の依存境界とエラーハンドリング/非同期/状態管理の契約を整理する。

## Why

- 現状 Projects は InMemory の Query 実装に直接依存しており、本番運用のロジック層（services/repositories）と乖離している。
- memos で確立したアーキテクチャ（ApplicationService 経由、Presenter/State/Controller の責務分離、明確なエラー/非同期方針）に合わせることで一貫性とテスト容易性が向上する。
- 将来的な性能最適化（ID 直取得、ページング、サーバーサイドソート）をロジック層に寄せられる。

## What Changes

- Controller を ProjectApplicationService の Port 経由に統一し、Query/Repository 直接依存を排除する。
- View は DI コンテナからサービスを取得して Controller に注入する（UI の API/VM 形状は不変）。
- 初期表示で一覧を必ず描画し、「全て」はフィルタなしとして扱う。
- CRUD 操作（作成/更新/削除）をすべて ApplicationService に委譲し、UI 側は `with_loading()` で実行中表示を統一する。
- サンプルデータの経路・ヘルパーを撤去し、実データはサービス単一路線へ統一する。
- エラーはユーザー通知（SnackBar）と `loguru` ログ出力の両方で扱う。

## Scope

- Projects View 内部の制御フローのみを変更する（Controller/State/Presenter の連携とサービス呼び出し）。
- ProjectApplicationService を利用するための Port（Protocol）定義と解決戦略（DI/`get_instance()` フォールバック）。
- 例外通知・ログ・非同期実行・ローディングフラグ・既知/未知エラーの整理。

## Non-Goals

- UI の見た目やコンポーネント API の変更は行わない（VM 形状含め完全に互換）。
- ロジック層の大規模改修は行わない（必要最小限の ApplicationService API 追加は可）。
- ルーティングやナビゲーション仕様の変更は行わない。

## Success Criteria

- Controller が ProjectApplicationService（Port）経由のみでデータ取得・検索・詳細取得を行うこと。
- 既存の `ProjectCardVM` / `ProjectDetailVM` の構造を変更せず、UI 側のコードは差分なしで動作すること。
- 例外時に UI 通知 + `loguru` での詳細ログが記録されること（既知/未知の分類方針に従う）。
- 重処理は UI スレッドをブロックしない（AsyncExecutor 相当のアダプタ経由）。
- 単体テストでモックサービス注入が可能であること（Query 直依存が無いこと）。

## Risks & Mitigations

| Risk                                        | Mitigation                                                     |
| ------------------------------------------- | -------------------------------------------------------------- |
| 既存 InMemoryQuery を前提としたテストが破綻 | Port を満たすテスト用アダプタを提供し差し替える                |
| 追加 API（get_by_id 等）の不足              | ApplicationService 側へ最小の取得 API を追加し、段階的に最適化 |
| 非同期実行の導入で状態競合                  | `with_loading()` と単一スレッド UI 更新の契約を厳守            |

## Open Questions

- ProjectApplicationService の正式 API: list/search/get_by_id の最小集合で足りるか（特に詳細パネル用）。
- 非同期アダプタの共通化: memos と同じ抽象（AsyncExecutor）で開始し、必要に応じて拡張。

## References

- Existing specs: `views-logic-binding`, `views-structure`, `view-state-management`, `base-view-contract`
- Code reference: `src/views/memos/*`（Controller/Query/Ordering/State/Presenter パターン）
