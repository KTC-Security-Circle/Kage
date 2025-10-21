# 用語管理システム (Terminology Management)

## 概要

Kageプロジェクトの用語管理システムは、社内固有の用語・略語・定義・参照情報を一元管理し、ユーザーの検索/参照体験とLLMへのコンテキスト提供を強化する機能です。

## 主な機能

### 1. 用語の管理

- **CRUD操作**: 用語の作成、読み取り、更新、削除
- **ステータス管理**: 草案 (DRAFT)、承認済み (APPROVED)、非推奨 (DEPRECATED)
- **メタデータ**: キー、タイトル、説明、出典URL
- **同義語**: 用語ごとに複数の同義語を登録可能
- **タグ付け**: 既存のタグシステムを活用した分類

### 2. 検索機能

- **キーワード検索**: キー、タイトル、説明での全文検索
- **同義語検索**: 同義語も含めた検索が可能
- **フィルタリング**: タグ、ステータスでのフィルタリング

### 3. インポート/エクスポート

- **CSV形式**: 表計算ソフトでの編集が容易
- **JSON形式**: プログラムからの処理が容易
- **バルク操作**: 大量の用語を一括でインポート/エクスポート

### 4. LLM連携

- **for_agents API**: エージェント向けのtop-k抽出
- **プロンプト整形**: LLMに渡しやすい形式で出力
- **タグフィルタ**: 特定のトピックに関連する用語のみを取得

## データモデル

### Term (用語)

```python
Term(
    id: UUID,
    key: str,              # 一意識別子（例: "LLM", "RAG"）
    title: str,            # 正式名称
    description: str,      # 説明・定義
    status: TermStatus,    # ステータス (DRAFT/APPROVED/DEPRECATED)
    source_url: str,       # 出典URL
    synonyms: List[Synonym],  # 同義語のリスト
    tags: List[Tag],       # タグのリスト
    created_at: datetime,
    updated_at: datetime,
)
```

### Synonym (同義語)

```python
Synonym(
    id: UUID,
    text: str,        # 同義語のテキスト
    term_id: UUID,    # 所属する用語のID
)
```

## 使用方法

### Serviceの取得

```python
from logic.unit_of_work import SqlModelUnitOfWork
from logic.services import TerminologyService

with SqlModelUnitOfWork() as uow:
    service = uow.get_service(TerminologyService)
    
    # 用語を作成
    term = service.create(TermCreate(
        key="LLM",
        title="大規模言語モデル",
        description="Large Language Modelの略称",
        status=TermStatus.APPROVED,
    ))
```

### 検索

```python
# キーワード検索
terms = service.search(query="学習")

# ステータスでフィルタリング
approved_terms = service.search(status=TermStatus.APPROVED)

# タグでフィルタリング
tech_terms = service.search(tags=[tech_tag_id])
```

### インポート/エクスポート

```python
from pathlib import Path

# JSONエクスポート
service.export_to_json(Path("terms.json"))

# JSONインポート
result = service.import_from_json(Path("terms.json"))
print(f"成功: {result.success_count}件, 失敗: {result.failed_count}件")
```

### LLM連携

```python
# エージェント用にtop-k抽出
terms = service.for_agents_top_k(
    query="機械学習",
    k=5,
    tags=[ml_tag_id],
)

# プロンプト用テキスト生成
prompt_context = "\n".join(term.to_prompt_text() for term in terms)
```

## データフォーマット

### CSV形式

```csv
key,title,description,status,source_url,synonyms,tags
LLM,大規模言語モデル,Large Language Modelの略称,approved,https://...,大規模言語モデル;Large Language Model,技術;AI
```

### JSON形式

```json
[
  {
    "key": "LLM",
    "title": "大規模言語モデル",
    "description": "Large Language Modelの略称",
    "status": "approved",
    "source_url": "https://...",
    "synonyms": ["大規模言語モデル", "Large Language Model"],
    "tags": ["技術", "AI"]
  }
]
```

## バックアップと復元

### バックアップ手順

1. 全用語をエクスポート

```python
service.export_to_json(Path("backup_terms.json"))
```

2. エクスポートファイルを安全な場所に保存

### 復元手順

1. バックアップファイルをインポート

```python
result = service.import_from_json(Path("backup_terms.json"))
```

2. インポート結果を確認

```python
if result.failed_count > 0:
    print("エラーが発生しました:")
    for error in result.errors:
        print(f"  - {error}")
```

## 制限事項

### 現在の制限

- **UI未対応**: 現在、UIは実装されていません。将来的に別提案で対応予定です。
- **ベクトル検索**: 初期段階ではキーワード検索のみをサポート。ベクトル検索は将来的な拡張として抽象インターフェースを準備済み。
- **同義語展開**: 検索時の同義語展開は単純な部分一致。より高度な展開は今後の改善項目。
- **並行編集**: 複数ユーザーによる同時編集の競合解決機能はありません。

### パフォーマンス

- **小規模～中規模**: 1,000件程度までの用語は問題なく動作
- **大規模**: 10,000件を超える場合はベクトル検索の導入を検討

## 将来の拡張

### Vector Index

将来的にベクトル検索を導入する場合、`AbstractVectorIndex`インターフェースを実装します:

```python
from logic.services.vector_index import AbstractVectorIndex

class FAISSVectorIndex(AbstractVectorIndex):
    # FAISS実装
    ...
```

### 多言語対応

現在は日本語のみですが、将来的に多言語対応を追加可能:

```python
Term(
    ...,
    locale: str,  # "ja", "en", etc.
)
```

## トラブルシューティング

### インポート失敗

- **原因**: 重複キー、フォーマットエラー
- **対処**: `ImportResult.errors`を確認し、該当行を修正

### 検索結果が空

- **原因**: ステータスフィルタが厳しすぎる、タグが設定されていない
- **対処**: フィルタ条件を緩和、またはタグを設定

### パフォーマンス低下

- **原因**: 用語数が多い、同義語が多い
- **対処**: インデックスの最適化、ベクトル検索への移行を検討

## 関連ドキュメント

- [アーキテクチャ設計](../dev/architecture-design.md)
- [リポジトリガイド](../dev/logic-testing-coverage/repository.md)
- [サービスガイド](../dev/logic-testing-coverage/service.md)
