# Tasks: organize-view-layer

<!-- OPENSPEC:START -->

## Ordered Task List

1. [x] Create spec skeletons for: views-structure / view-state-management / views-logic-binding / view-components-guidelines / base-view-contract (routing deferred)
2. [x] Define ADDED requirements + at least 1 Scenario each (happy path) for views-structure
3. [x] Add Scenarios for edge/error (missing service dependency) ※ invalid route は defer（ルーティング out-of-scope）
4. [x] (Removed) Define routing-and-navigation requirements → Deferred; out-of-scope per updated proposal
5. [x] Define view-state-management requirements (immutable dataclass state objects, update flow, loading/error flags)
6. [x] Define views-logic-binding requirements (Application Service boundary, prohibition of business logic in View, error notification contract)
7. [x] Define view-components-guidelines requirements (props/state split, naming, reusability rules, side-effect policy)
8. [x] Add cross-references between specs where dependencies exist (e.g. BaseView ↔ state-management, logic-binding ↔ components-guidelines)
9. [x] Add new requirements for async executor adapter, error categories, stable keys, cleanup lifecycle (route params deferred)
10. [x] Run strict validation (`openspec validate organize-view-layer --strict`) and resolve all issues（ルーティング関連要件は除外済みであることを確認）
11. [x] Prepare design.md only if additional architectural trade-offs emerge during authoring (update if BaseView impacts architecture)
12. [x] Final review: ensure acceptance criteria in proposal map to at least one requirement (routing out-of-scope, test code creation excluded)
13. [x] Document out-of-scope (router implementation & test code) explicitly in proposal

<!-- OPENSPEC:END -->
