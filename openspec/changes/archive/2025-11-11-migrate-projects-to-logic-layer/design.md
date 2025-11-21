# Design: Projects View x Logic Layer Integration (UI preserved)

## Architectural Overview

Align Projects with the memos pattern:

- View: 構築・イベント配線・ハンドラ注入（UI ロジックのみ）
- Controller: 状態更新の調停、ApplicationService(Port) 呼び出し、Presenter への橋渡し
- State: 表示状態（検索条件、選択、並び順、loading/error）を dataclass で保持
- Presenter: ドメイン →ViewModel の変換（UI は Presenter の VM だけを扱う）
- Logic layer: ProjectApplicationService 経由で Repository へアクセス

UI は変更せず、Controller の依存だけを Query→Service(Port) へ移す。

## Key Contracts

- Port: `ProjectApplicationPort`（Protocol）

  - `list_projects(keyword: str = "", status: ProjectStatus | None = None) -> list[ProjectRead]`
  - `get_project_by_id(project_id: UUID) -> ProjectRead | None`（詳細パネル最適化のため）
  - 将来的に `search`, `paginate`, `order_by` はサービス側で最適化（Controller は条件を渡すのみ）

- Dependency Resolution

  - コンストラクタ DI を優先（テスト注入容易化）
  - 未注入時は `ProjectApplicationService.get_instance()` をフォールバック解決（views-logic-binding に準拠）

- Error & Async Policy

  - 既知ドメイン例外: 説明的メッセージを SnackBar（または AlertDialog）で通知、`loguru` で詳細を記録
  - 未知例外: 汎用メッセージ + 例外ログ
  - 重処理は `AsyncExecutor.run(callable)` 経由で UI スレッドをブロックしない
  - State: `loading` を確実に往復させる（`with_loading()` ヘルパ）

- UI Stability
  - `ProjectCardVM` / `ProjectDetailVM` の構造・フィールドは変更しない
  - コンポーネントはハンドラ（Callable/Protocol）だけを受け取り、サービス/ルータへ直接依存しない

## Migration Strategy

1. Port 追加（memos の `MemoApplicationPort` と同様の最小 API を定義）
2. Controller から InMemoryQuery 直接依存を排除し Port へ置換
3. 詳細取得の線形探索を `get_project_by_id` 呼び出しへ最適化（サービスが提供する場合）
4. 例外ハンドリング/ローディング/未知例外のポリシーを明示化
5. テストはサービスモック注入へ切り替え（Query モックは非推奨）

## Alternatives Considered

| 代替                             | 不採用理由                                                                  |
| -------------------------------- | --------------------------------------------------------------------------- |
| Query を Controller でラップする | 境界が曖昧で、views-logic-binding の原則（View→ApplicationService）に反する |
| View から直接 Service 呼び出し   | Controller が責務集中点でなくなる。テストしづらい                           |

## Impacted Components

- `src/views/projects/controller.py`（依存の差し替えとエラーポリシー）
- `src/views/projects/query.py`（InMemory 実装のテスト専用化/非推奨化）
- `src/views/projects/state.py`（loading/error の契約徹底、必要に応じて微修正）
- `src/views/projects/presenter.py`（VM 形状は維持、変換のみ）

## Compatibility

UI 公開 API/VM は維持されるため、画面/コンポーネントの呼び出し側の変更は不要。
