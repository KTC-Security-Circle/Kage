# 開発者向けクイックリファレンス

新規開発者が迷わないための要点をまとめた簡潔なガイドです。

## 🚀 環境構築

```bash
# poethepoetをグローバルにインストール
uv tool install poethepoet

# 初回セットアップ
poe setup
```

## 📝 ブランチ作成

**必ず[ブランチ命名規則](../docs/branch_naming.md)に従ってください**

```bash
# 基本形: <type>/<slug>
git checkout -b feature/task-filter
git checkout -b fix/textarea-overflow
git checkout -b chore/update-deps

# イシュー番号付き: <type>/<issue-number>-<slug>
git checkout -b fix/123-null-pointer
```

## 🛠️ 開発フロー

```bash
# 開発モード起動
poe app-dev

# コード品質チェック
poe check

# 自動修正
poe fix

# テスト実行
poe test
```

## 📂 アーキテクチャ

- `src/views/`: UI 層（Flet）
- `src/logic/`: ビジネスロジック層
- `src/models/`: データモデル層
- `src/agents/`: AI/Agent 層

## 📖 詳細ドキュメント

- [コントリビューションガイド](../CONTRIBUTING.md)
- [ブランチ命名規則](../docs/branch_naming.md)
- [アーキテクチャ設計](../docs/architecture-design.md)
- [タスクランナーガイド](../docs/task_runner.md)

---

🎯 **迷ったら**: `fix/明確な短い説明` か `chore/...` に寄せる
