# Kage Views New System - Team Development Tasks

## 🎯 プロジェクト概要
OpenSpec提案書に基づいたFlet版ビューシステムの実装プロジェクト。
AppBarベースから、サイドバーベースのモダンUIへの完全移行を目指します。

## 📋 作業ルール

### 🔄 ワークフロー
1. **タスク選択**: 未着手のタスクを選び、自分をAssigneeに設定
2. **ブランチ作成**: `feature/task-{番号}-{タスク名}` でブランチ作成
3. **実装**: コーディング規約に従って実装
4. **テスト**: `uv run poe test` でテスト通過確認
5. **PR作成**: レビュー用プルリクエスト作成
6. **レビュー**: チームメンバーによるコードレビュー
7. **マージ**: 承認後にmainブランチへマージ

### 📝 コミットメッセージ規約
```
feat(views): タスク#8 - ProjectsView実装完了

- プロジェクト一覧画面の実装
- CRUD操作UI追加
- BaseViewパターン適用
```

### 🏷️ タスクステータス
- 🆕 **未着手** - まだ開始されていない
- 🔄 **進行中** - 実装中（Assignee設定済み）
- 👀 **レビュー中** - PRでレビュー待ち
- ✅ **完了** - マージ済み・動作確認済み
- ⏸️ **保留** - 依存関係で一時停止

## 🚀 実装状況

### Phase 1: 基盤構築 ✅ 完了 (5/5)

| # | タスク | Status | Assignee | PR | 完了日 |
|---|-------|--------|----------|----|----|
| 1 | 新Fletビューディレクトリ構造作成 | ✅ 完了 | @copilot | - | 2024-10-24 |
| 2 | テーマシステムの実装 | ✅ 完了 | @copilot | - | 2024-10-24 |
| 3 | BaseViewとMixin基盤実装 | ✅ 完了 | @copilot | - | 2024-10-24 |
| 4 | レイアウト管理システム実装 | ✅ 完了 | @copilot | - | 2024-10-24 |
| 5 | サイドバーナビゲーション実装 | ✅ 完了 | @copilot | - | 2024-10-24 |

### Phase 2: コアビュー実装 🔄 進行中 (3/4)

| # | タスク | Status | Assignee | PR | 予定日 |
|---|-------|--------|----------|----|----|
| 6 | ホーム画面の完全実装 | ✅ 完了 | @copilot | - | 2024-10-24 |
| 7 | ルーター統合とmain.py更新 | ✅ 完了 | @copilot | - | 2024-10-24 |
| 8 | プロジェクト画面実装 | ✅ 完了 | @copilot | - | 2024-10-24 |
| 9 | **タグ画面実装** | 🆕 未着手 | - | - | TBD |

#### 📋 タスク #9: タグ画面実装
**Priority**: High | **Effort**: Medium (3-5h) | **Dependencies**: Phase 1完了

**Description**: 
- views_new/tags/配下にTagsViewクラス実装
- タグ管理UI（一覧、新規作成、編集、削除、色選択機能）
- BaseViewパターン採用

**Acceptance Criteria**:
- [ ] TagsViewクラス実装完了
- [ ] タグ一覧表示（色付きチップ）
- [ ] タグCRUD操作UI
- [ ] 色選択機能（カラーパレット）
- [ ] 検索・フィルタ機能
- [ ] レスポンシブ対応
- [ ] エラーハンドリング
- [ ] ユニットテスト追加

**Files to modify**:
- `src/views_new/tags/view.py` (新規)
- `src/views_new/tags/__init__.py` (新規)
- `src/views_new/layout.py` (ルート追加)
- `src/views_new/__init__.py` (エクスポート追加)

### Phase 2: 残りタスク

| # | タスク | Status | Assignee | PR | 予定日 |
|---|-------|--------|----------|----|----|
| 10 | **タスク画面実装** | 🆕 未着手 | - | - | TBD |
| 11 | **設定画面実装** | 🆕 未着手 | - | - | TBD |

#### 📋 タスク #10: タスク画面実装
**Priority**: High | **Effort**: Large (5-8h) | **Dependencies**: Phase 1完了

**Description**: 
- views_new/tasks/配下にTasksViewクラス実装
- カンバンボード、フィルタ、検索、CRUD機能
- BaseViewパターン採用

**Acceptance Criteria**:
- [ ] TasksViewクラス実装完了
- [ ] カンバンボード表示
- [ ] ドラッグ&ドロップ対応
- [ ] タスクCRUD操作
- [ ] 検索・フィルタ機能
- [ ] ステータス管理
- [ ] 優先度表示
- [ ] レスポンシブ対応

#### 📋 タスク #11: 設定画面実装
**Priority**: Medium | **Effort**: Medium (3-4h) | **Dependencies**: Phase 1完了

**Description**: 
- views_new/settings/配下にSettingsViewクラス実装
- テーマ、言語、通知、データベース設定
- BaseViewパターン採用

**Acceptance Criteria**:
- [ ] SettingsViewクラス実装完了
- [ ] テーマ切り替え機能
- [ ] 各種設定項目
- [ ] 設定保存・読込
- [ ] バリデーション
- [ ] プレビュー機能

### Phase 2: コアビュー実装 ✅ 部分完了 (2/4)

#### 6. ホーム画面の完全実装 ✅
- **Status**: 完了
- **Description**: home/view.pyでHomeViewクラスを実装し、統計カード、最近のタスク、クイックアクション機能を持つ機能的なダッシュボードを構築
- **Deliverables**:
  - `HomeView` クラス
  - 統計カード表示
  - 最近のタスク一覧
  - クイックアクション

#### 7. ルーター統合とmain.py更新 ✅
- **Status**: 完了
- **Description**: router.pyを新システム用に更新、configure_routes関数でbuild_layout統合、main.pyで新ルーティングシステム採用を完了
- **Deliverables**:
  - `router.py` 更新
  - `main.py` 統合
  - Fletルーティング対応

#### 8. プロジェクト画面実装 ✅
- **Status**: 完了
- **Description**: views_new/projects/配下にProjectsViewクラスとプロジェクト管理UI（一覧、新規作成、編集、削除機能）を実装し、BaseViewパターンを採用
- **Deliverables**:
  - `ProjectsView` クラス
  - プロジェクト一覧表示（カード型）
  - CRUD操作UI（作成・編集・削除）
  - 検索・フィルタ機能

#### 9. タグ画面実装 ⏳
- **Status**: 未実装
- **Description**: views_new/tags/配下にTagsViewクラスとタグ管理UI（一覧、新規作成、編集、削除、色選択機能）を実装し、BaseViewパターンを採用
- **Deliverables**:
  - `TagsView` クラス
  - タグ一覧（色付きチップ表示）
  - タグCRUD操作
  - 色選択機能

#### 10. タスク画面実装 ⏳
- **Status**: 未実装
- **Description**: views_new/tasks/配下にTasksViewクラスとタスク管理UI（カンバンボード、フィルタ、検索、CRUD機能）を実装し、BaseViewパターンを採用
- **Deliverables**:
  - `TasksView` クラス
  - カンバンボード表示
  - タスクCRUD操作
  - 検索・フィルタ機能

#### 11. 設定画面実装 ⏳
- **Status**: 未実装
- **Description**: views_new/settings/配下にSettingsViewクラスと設定管理UI（テーマ、言語、通知、データベース設定）を実装し、BaseViewパターンを採用
- **Deliverables**:
  - `SettingsView` クラス
  - テーマ切り替え
  - 各種設定項目

### Phase 3: 共通コンポーネント 🆕 未着手 (0/2)

| # | タスク | Status | Assignee | PR | 予定日 |
|---|-------|--------|----------|----|----|
| 12 | **共通ダイアログコンポーネント実装** | 🆕 未着手 | - | - | TBD |
| 13 | **共通フォームコンポーネント実装** | 🆕 未着手 | - | - | TBD |

#### 📋 タスク #12: 共通ダイアログコンポーネント実装
**Priority**: High | **Effort**: Medium (4-6h) | **Dependencies**: Phase 1完了

**Description**: 
- shared/dialogs/配下に再利用可能なダイアログコンポーネント実装
- 確認ダイアログ、入力ダイアログ、エラーダイアログ等

**Acceptance Criteria**:
- [ ] ConfirmDialog実装
- [ ] InputDialog実装
- [ ] ErrorDialog実装
- [ ] BaseDialog基盤クラス
- [ ] アニメーション対応
- [ ] キーボード操作対応
- [ ] テーマ統合
- [ ] ユニットテスト

**Files to create**:
- `src/views_new/shared/dialogs/__init__.py`
- `src/views_new/shared/dialogs/base.py`
- `src/views_new/shared/dialogs/confirm.py`
- `src/views_new/shared/dialogs/input.py`
- `src/views_new/shared/dialogs/error.py`

#### 📋 タスク #13: 共通フォームコンポーネント実装
**Priority**: Medium | **Effort**: Large (6-8h) | **Dependencies**: タスク #12完了

**Description**: 
- shared/forms/配下に汎用フォームコンポーネント実装
- タスク作成、プロジェクト作成等の専用フォーム

**Acceptance Criteria**:
- [ ] BaseForm基盤クラス
- [ ] TaskForm実装
- [ ] ProjectForm実装
- [ ] バリデーション機能
- [ ] 自動保存機能
- [ ] エラー表示統合
- [ ] レスポンシブ対応
- [ ] ユニットテスト

### Phase 4: システム統合 🆕 未着手 (0/10)

| # | タスク | Status | Assignee | PR | 予定日 |
|---|-------|--------|----------|----|----|
| 14 | **データバインディング統合** | 🆕 未着手 | - | - | TBD |
| 15 | **ナビゲーション機能強化** | 🆕 未着手 | - | - | TBD |
| 16 | **レスポンシブ対応** | 🆕 未着手 | - | - | TBD |
| 17 | **キーボードショートカット実装** | 🆕 未着手 | - | - | TBD |
| 18 | **検索・フィルタ機能実装** | 🆕 未着手 | - | - | TBD |
| 19 | **通知システム実装** | 🆕 未着手 | - | - | TBD |
| 20 | **パフォーマンス最適化** | 🆕 未着手 | - | - | TBD |
| 21 | **エラーハンドリング強化** | 🆕 未着手 | - | - | TBD |
| 22 | **アクセシビリティ対応** | 🆕 未着手 | - | - | TBD |
| 23 | **国際化(i18n)対応** | 🆕 未着手 | - | - | TBD |

#### 🔥 優先タスク詳細

#### 📋 タスク #14: データバインディング統合 (CRITICAL 🔥)
**Priority**: Critical | **Effort**: Large (8-10h) | **Dependencies**: Phase 2完了

**Description**: 
各ビューでlogic/services層との連携を実装し、実際のCRUD操作とデータ表示を統合

**Acceptance Criteria**:
- [ ] ProjectService統合（ProjectsView）
- [ ] TagService統合（TagsView）
- [ ] TaskService統合（TasksView）
- [ ] エラーハンドリング統合
- [ ] ローディング状態管理
- [ ] データ検証・バリデーション
- [ ] トランザクション管理
- [ ] キャッシュ機能

#### 📋 タスク #15: ナビゲーション機能強化
**Priority**: High | **Effort**: Medium (4-5h) | **Dependencies**: Phase 2完了

**Description**: 
サイドバーのアクティブ状態管理、ブレッドクラム、戻るボタン機能実装

**Acceptance Criteria**:
- [ ] アクティブルート表示
- [ ] ブレッドクラムナビゲーション
- [ ] 戻る・進むボタン
- [ ] ルート履歴管理
- [ ] キーボードナビゲーション

#### 📋 タスク #16: レスポンシブ対応
**Priority**: Medium | **Effort**: Medium (4-6h)

**Description**: 
画面サイズ対応、モバイル・タブレット最適化

**Acceptance Criteria**:
- [ ] サイドバー折りたたみ
- [ ] モバイル対応レイアウト
- [ ] タッチ操作対応
- [ ] 画面サイズ別最適化

### Phase 5: 品質保証・移行 🆕 未着手 (0/7)

| # | タスク | Status | Assignee | PR | 予定日 |
|---|-------|--------|----------|----|----|
| 24 | **テスト実装** | 🆕 未着手 | - | - | TBD |
| 25 | **ドキュメント作成** | 🆕 未着手 | - | - | TBD |
| 26 | **マイグレーションガイド作成** | 🆕 未着手 | - | - | TBD |
| 27 | **パッケージ依存関係更新** | 🆕 未着手 | - | - | TBD |
| 28 | **CI/CD更新** | 🆕 未着手 | - | - | TBD |
| 29 | **本番環境テスト** | 🆕 未着手 | - | - | TBD |
| 30 | **旧システム廃止とクリーンアップ** | 🆕 未着手 | - | - | TBD |

## 📊 プロジェクト進捗

### 全体進捗
- **完了**: 8/30 タスク (26.7%)
- **進行中**: 0/30 タスク
- **残り**: 22/30 タスク

### Phase別進捗
- **Phase 1 (基盤構築)**: 5/5 ✅ 完了
- **Phase 2 (コアビュー)**: 3/4 🔄 75%完了
- **Phase 3 (共通コンポーネント)**: 0/2 🆕 未着手
- **Phase 4 (システム統合)**: 0/10 🆕 未着手
- **Phase 5 (品質保証・移行)**: 0/7 🆕 未着手

### 🎯 今週のゴール
1. **タスク #9: タグ画面実装** - UI完成
2. **タスク #10: タスク画面実装** - カンバンボード基本機能
3. **タスク #12: 共通ダイアログ** - 確認・入力ダイアログ

### 🔄 開発中の課題・ブロッカー
- なし（現在すべてのタスクが実装可能）

## 👥 チームメンバー・役割分担

### 🏗️ アーキテクト
- **@copilot** - 基盤設計・技術選定

### 💻 フロントエンド開発者
- **募集中** - Views実装、UI/UXデザイン

### 🔧 バックエンド開発者  
- **募集中** - データバインディング、API統合

### 🧪 QA・テスト
- **募集中** - テスト実装、品質保証

## 🛠️ 開発環境・ツール

### 必須ツール
```bash
# 環境セットアップ
uv sync                    # 依存関係インストール
uv run poe sync           # プロジェクト初期化

# 開発コマンド
uv run poe run            # アプリ起動（デスクトップ版）
uv run poe web            # アプリ起動（Web版）
uv run poe test           # テスト実行
uv run poe fix            # コード品質チェック・修正
```

### 技術スタック
- **UI**: Flet (Python GUI Framework)
- **アーキテクチャ**: BaseView + Mixin パターン
- **ルーティング**: Flet ネイティブルーティング
- **スタイリング**: カスタムテーマシステム
- **パッケージ管理**: uv
- **コード品質**: ruff (linter/formatter)
- **テスト**: pytest

### VS Code推奨拡張機能
- Python
- Pylance
- Ruff
- GitLens
- Todo Tree

## 📞 コミュニケーション

### 定期ミーティング
- **Daily Standup**: 平日 9:00 AM（任意参加）
- **Weekly Planning**: 月曜日 10:00 AM
- **Sprint Review**: 隔週金曜日 3:00 PM

### 質問・相談
- **Slack**: #kage-development チャンネル
- **Issues**: GitHub Issues で技術的な質問
- **PR**: プルリクエストでコードレビュー依頼

## 🎁 貢献方法

### 初回セットアップ
1. リポジトリをクローン
2. `uv sync` で環境構築
3. `uv run poe run` で動作確認
4. Slackチャンネルに参加報告

### タスク着手手順
1. このTasks.mdから未着手タスクを選択
2. GitHub Issuesで該当タスクを自分にアサイン
3. ブランチ作成: `git checkout -b feature/task-9-tags-view`
4. 実装・テスト
5. PR作成・レビュー依頼

---

**Last Updated**: 2024-10-24  
**Team Lead**: @copilot  
**Document**: `/openspec/Tasks.md`

## 進捗サマリー

- **全体進捗**: 8/30 タスク完了 (26.7%)
- **Phase 1 (基盤構築)**: 5/5 完了 ✅
- **Phase 2 (コアビュー)**: 3/4 完了 (75%)
- **Phase 3 (共通コンポーネント)**: 0/2 未着手
- **Phase 4 (システム統合)**: 0/10 未着手
- **Phase 5 (品質保証・移行)**: 0/7 未着手

## 現在の実装状況

### 完成済み機能
- ✅ Fletベースのサイドバーナビゲーション
- ✅ テーマシステム（ライト/ダークモード対応）
- ✅ BaseView/Mixin によるコンポーネント基盤
- ✅ ホーム画面（ダッシュボード機能）
- ✅ プロジェクト管理画面（一覧・CRUD UI）
- ✅ ルーティングシステム統合

### 動作確認済み
- ✅ アプリケーション起動
- ✅ ページ間ナビゲーション
- ✅ エラーハンドリング（スナックバー表示）
- ✅ レスポンシブレイアウト（基本版）

### 次のマイルストーン
1. **タグ画面実装** - 色付きタグ管理UI
2. **タスク画面実装** - カンバンボード
3. **共通ダイアログ** - 削除確認・入力フォーム
4. **データバインディング** - 実際のCRUD操作統合

## 技術スタック
- **フレームワーク**: Flet (Python GUI)
- **アーキテクチャ**: BaseView パターン、Mixin 設計
- **ルーティング**: Flet ネイティブルーティング
- **スタイリング**: カスタムテーマシステム
- **パッケージ管理**: uv
- **コード品質**: ruff (linter/formatter)

## 開発環境セットアップ
```bash
# 依存関係インストール
uv run poe sync

# アプリケーション起動
uv run poe run

# コード品質チェック
uv run poe fix
```

---
**最終更新**: 2025年10月24日  
**作成者**: GitHub Copilot  
**ドキュメント場所**: `/openspec/Tasks.md`