# モデル一覧

## データベース用 モデル

データベースのテーブルに対応するモデルです。
SQLModelを継承して定義されており、データベースのCRUD操作に使用されます。

基本各モデルは以下の形で定義されます。

- Base: 基本的なモデルクラス
- Main: テーブル定義用のクラス （DB操作時に使用）
- Create: 新規作成用のモデルクラス
- Read: 読み取り用のモデルクラス
- Update: 更新用のモデルクラス

この設計は、データの整合性と操作の明確化を目的としています。

::: src.models.task
::: src.models.project
::: src.models.tag
::: src.models.task_tag
::: src.models.memo
