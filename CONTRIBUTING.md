# Kage への貢献

このプロジェクトへの貢献に興味を持っていただき、ありがとうございます。
バグ報告、機能提案、プルリクエストなど、あらゆる形の貢献を歓迎します。

## 開発ワークフロー

1. **Issue の確認**: まず、[Issue Tracker](https://github.com/KTC-Security-Circle/Kage/issues) を確認し、同様の Issue がないか確認してください。なければ新しい Issue を作成します。

2. **リポジトリのフォーク**: このリポジトリをフォークします。

3. **ブランチの作成**: 新しいブランチを作成します。ブランチ名は[ブランチ命名規則](docs/branch_naming.md)に従ってください。

   ```bash
   # 例: 新機能の場合
   git checkout -b feature/new-task-button

   # 例: バグ修正の場合
   git checkout -b fix/textarea-overflow

   # 例: イシュー番号を含める場合
   git checkout -b feature/123-task-filter
   ```

4. **poethepoet のインストール**: グローバルに poethepoet をインストールします（未インストールの場合）。

   ```bash
   # poethepoetをグローバルにインストール
   uv tool install poethepoet
   ```

5. **環境セットアップ**: poethepoet タスクランナーを使用した初回セットアップを実行します。

   ```bash
   # 初回セットアップ（依存関係同期 + DB更新）
   poe setup
   ```

6. **コードの変更**: コーディング規約に従って、コードの追加・修正を行います。

7. **テストとコード品質チェック**: 変更によって既存の機能が壊れていないことを確認します。

   ```bash
   # 品質チェック（lint + format-check + type-check）
   poe check

   # 自動修正（lint-fix + format）
   poe fix

   # テスト実行
   poe test
   ```

8. **開発中の動作確認**: アプリケーションを起動して動作を確認します。

   ```bash
   # 開発モード（ホットリロード）
   poe app-dev
   ```

9. **コミット**: 変更内容をコミットします。コミットメッセージは分かりやすく記述してください。

10. **プルリクエストの作成**: フォークしたリポジトリから、このリポジトリの `main` ブランチに対してプルリクエストを作成します。プルリクエストのテンプレートに従い、変更内容を説明してください。

詳細なタスクコマンドについては[タスクランナーガイド](docs/task_runner.md)を参照してください。

## コーディング規約

- **静的解析**: `ruff` を使用した静的解析とフォーマットを適用します。`pre-commit`フックが自動で実行します。
- **命名規則**:
  - クラス名: `PascalCase`
  - 関数・変数名: `snake_case`
- **Docstring**: クラスや公開関数には、Google スタイルの docstring を記述してください。

  ```python
  def my_function(param1: int, param2: str) -> bool:
      """関数の概要説明.

      Args:
          param1: 引数1の説明.
          param2: 引数2の説明.

      Returns:
          戻り値の説明.
      """
      # ...
  ```

- **型ヒント**: すべての関数・メソッドの引数と戻り値に型ヒントを付けてください。
- **コメント**: 複雑なロジックや重要な処理には、日本語で簡潔なコメントを記述してください。

ご協力に感謝します！
