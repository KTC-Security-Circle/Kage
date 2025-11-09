# Design: organize-view-layer

<!-- OPENSPEC:START -->

## Problem Statement

View 実装とロジック層の責務境界が曖昧で、画面ごとの構造・命名・状態管理が統一されていない。可読性とテスト容易性、将来の拡張性（画面追加/差し替え）を阻害している。

## Goals

- View は UI とユーザインタラクションに集中し、ビジネスロジックは Application Service に委譲する
- 画面/コンポーネントの配置・命名・分割方針を標準化
- ルーティング・状態管理・エラーハンドリングを共通化

## Non-Goals

- 高度な UI アニメーションや DnD 仮想化の最適化
- ディープな DI コンテナ導入（必要になれば後続変更で対応）

## Architecture Overview

- 層分離
  - View (Flet): 入力収集、表示、イベント → 意図（Intent）発行
  - Application (Python): バリデーション、トランザクション、サービス編成
  - Service/Repository/Model: ドメイン規則、データ永続化
- 取得経路
  - Application Service は `*.get_instance()` または明示の依存注入で取得
  - 例外は View で捕捉してユーザ通知 + ログ（`loguru`）
- 状態
  - View は dataclass の State を 1 つ持ち、`loading/error_message` を標準化
  - コンポーネントは stateless 優先、必要時のみローカル state
- NOTE: 本変更では Router の具体的な実装詳細（ルート解決、パラメータパース、`page.on_route_change` ハンドラ）は対象外。後続の専用変更で扱う。

## Alternatives Considered

1. DI コンテナ導入（Provider パターン）

- Pros: テスト容易、差し替え容易
- Cons: 現段階で導入コストが大きい
- Decision: 後続変更候補。まずは `get_instance()` で統一

1. Fat Component（コンポーネントが Service を直接保持）

- Pros: 実装が早い
- Cons: 再利用とテスト、責務境界が崩れる
- Decision: 採用しない

## Trade-offs

- シンプルさを優先し、段階的に抽象を導入
- 既存コード（例: `MemoApplicationService`）に合わせた規約化で移行コストを抑制

## Impact & Migration

- 新規実装: 本ルールに従う
- 既存実装: 段階的にファイル移動/命名揃え（破壊的変更は次フェーズで）

## Validation Strategy

- 仕様は変更内 `specs/*` のシナリオで検証
- 実装に着手する際は `views/*` にスケルトンを追加し、View 内の責務境界/状態管理/コンポーネント分割を確認（Router 動作検証は別変更で実施）

<!-- OPENSPEC:END -->
