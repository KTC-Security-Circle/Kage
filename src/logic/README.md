# Logic 層 - ビジネスロジック管理

Kage アプリケーションのビジネスロジックを管理する中心的な層です。クリーンアーキテクチャと DDD（ドメイン駆動設計）の原則に基づいて設計されています。

## 📁 モジュール構成

### Application Service 層 (`application/`)

**目的**: View 層から Session 管理を分離し、ビジネスロジックの調整を行う

- `base.py` - Application Service 基底クラス
- `task_application_service.py` - タスク管理の Application Service
- `project_application_service.py` - プロジェクト管理の Application Service
- `tag_application_service.py` - タグ管理の Application Service
- `task_tag_application_service.py` - タスク-タグ関連付けの Application Service

**特徴**:

- Unit of Work パターンによるトランザクション管理
- Command/Query パターンの実装
- View 層からの複雑な操作の簡素化

### Command 層 (`commands/`)

**目的**: データ変更操作のためのコマンドオブジェクト（CQRS パターン）

- `task_commands.py` - タスク操作コマンド（作成、更新、削除、ステータス変更）
- `project_commands.py` - プロジェクト操作コマンド
- `tag_commands.py` - タグ操作コマンド
- `task_tag_commands.py` - タスク-タグ関連付けコマンド

**特徴**:

- データ変更操作の明確な意図表現
- バリデーション機能の包含
- DTO としてのデータ転送機能

### Query 層 (`queries/`)

**目的**: データ取得操作のためのクエリオブジェクト（CQRS パターン）

- `task_queries.py` - タスク取得クエリ（ステータス別、ID 指定、件数取得等）
- `project_queries.py` - プロジェクト取得クエリ
- `tag_queries.py` - タグ取得クエリ
- `task_tag_queries.py` - タスク-タグ関連取得クエリ

**特徴**:

- 読み込み専用操作の分離
- 検索条件の明確化
- パフォーマンス最適化の基盤

### Service 層 (`services/`)

**目的**: 具体的なビジネスロジックとデータ操作の実装

- `base.py` - サービス基底クラスとカスタム例外
- `task_service.py` - タスクビジネスロジック
- `project_service.py` - プロジェクトビジネスロジック
- `tag_service.py` - タグビジネスロジック
- `task_tag_service.py` - タスク-タグ関連ビジネスロジック

**特徴**:

- Repository 層との協調
- ビジネスルールの実装
- エラーハンドリングとログ記録

### Repository 層 (`repositories/`)

**目的**: データアクセスの抽象化と CRUD 操作の提供

- `base.py` - リポジトリ基底クラス（汎用 CRUD 操作）
- `task.py` - タスクデータアクセス
- `project.py` - プロジェクトデータアクセス
- `tag.py` - タグデータアクセス
- `task_tag.py` - タスク-タグ関連データアクセス

**特徴**:

- SQLModel を使用した ORM 操作
- データアクセスロジックの分離
- 型安全なデータ操作

### 依存性注入・ファクトリ

**目的**: オブジェクトの生成と依存関係の管理

- `container.py` - Application Service の依存性注入コンテナ
- `factory.py` - Repository・Service ファクトリクラス
- `unit_of_work.py` - Unit of Work パターン実装（トランザクション管理）

**特徴**:

- シングルトンパターンによるインスタンス管理
- トランザクション境界の適切な管理
- テスタビリティの向上

## 🔄 データフロー

```text
View層
    ↓ (Command/Query)
Application Service層
    ↓ (ビジネスロジック調整)
Service層
    ↓ (データ操作要求)
Repository層
    ↓ (SQL実行)
Database
```

## 🛡️ 設計原則

1. **単一責任の原則**: 各層は明確に定義された責任を持つ
2. **依存性逆転**: 抽象に依存し、具象には依存しない
3. **関心事の分離**: Command/Query での操作分離
4. **トランザクション管理**: Unit of Work パターンでの一貫性保証

## 📝 使用例

```python
# Application Serviceの使用例
from logic.container import ServiceContainer
from logic.commands.task_commands import CreateTaskCommand

# コンテナからサービス取得
container = ServiceContainer()
task_app_service = container.get_task_application_service()

# コマンドでタスク作成
command = CreateTaskCommand(title="新しいタスク", description="説明")
created_task = task_app_service.create_task(command)
```

この設計により、各層の責任が明確になり、保守性とテスタビリティの高いアプリケーションを実現しています。
