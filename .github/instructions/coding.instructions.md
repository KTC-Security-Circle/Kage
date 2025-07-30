---
applyTo: "**/*.py"
---

# Coding Instructions

Python のコーディングに関するガイドライン。
Python のコードを生成する場合は必ずこのガイドラインに従うこと。

## コーディング規約と開発標準

以下の規約を厳守すること。

    設計原則:

        YAGNI (You Aren't Gonna Need It): 現在必要とされていない機能は実装しないこと。将来を予測した先行実装は避ける。

        DRY (Don't Repeat Yourself): コードの重複を避け、共通ロジックは関数やクラスに切り出して再利用すること。

        KISS (Keep It Simple, Stupid): 複雑な解決策よりも、シンプルで理解しやすいコードを優先すること。

    フォーマットと静的解析:

        フォーマッタ兼リンターは Ruff を使用する。設定は pyproject.toml に従うこと。

        コードを変更した場合は `poe check (ruff check と ruff format --fix の同時実行タスク)` でフォーマットとチェックを実行し、警告やエラーを修正すること。

    型ヒント (Type Hinting):

        全ての関数・メソッドの引数と戻り値に型ヒントを付与すること。

        typing.Any, typing.Optional の使用は最小限に留めること。

        アプリ固有のデータ構造には、カスタム型（TypedDict, dataclasses等）を積極的に定義して使用すること。

    命名規則:

        変数・関数: snake_case

        クラス: PascalCase

        定数: UPPER_SNAKE_CASE

    モジュール構成:

        srcレイアウトを採用し、srcディレクトリ以下に全てのコードを配置すること。

        関心事を分離するため、機能ごとにモジュールを分割すること（例: views, logic, models, agents）。

        モジュール間の循環参照は禁止する。

    コメントとDocstring:

        AIが生成したコメントの先頭には [AI GENERATED] を付けること。

        複雑なロジックには処理内容を説明するコメントを記述すること。

        全ての公開クラスと関数には、GoogleスタイルのDocstringを記述すること。

    エラーハンドリング:

        try...except ブロックでは具体的な例外を捕捉し、汎用的な except Exception: は避けること。

        exceptionのメッセージは具体的で問題の特定に役立つ情報を含め、 loguru ライブラリの `logger.exception` を使用してログに記録すること。

        ユーザーへのエラー通知には、Fletの AlertDialog や SnackBar を使用すること。

    設定と秘匿情報:

        秘匿情報はコードに直接記述せず、.env ファイルで管理すること。

        .gitignore により、.env がリポジトリに含まれないことを確認すること。

        .env ファイルは `env.py` の `setup_environment` 関数を使用して読み込むこと。

    ロギング:

        ロギングには Loguru を使用すること。

        ログレベル（DEBUG, INFO, WARNING, ERROR）を適切に使い分け、デバッグや問題追跡に役立つ情報を出力すること。

        Loguru の設定は `logging_conf.py` に定義し、 `setup_logger` 関数を使用してアプリケーション全体で統一すること。
