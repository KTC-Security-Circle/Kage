"""メモ→タスク変換エージェント用プロンプト定義。"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

classification_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたは GTD の Clarify/Organize フェーズを支援するアナリストです。
メモの背景・目的・行動粒度を読み解き、idea / task / project のどれに該当するかを判断してください。
分類理由では「なぜその判断に至ったのか」を端的に説明し、project と判断する場合は
適切なプロジェクト名の案を添えてください。
応答は JSON 形式で、decision・reason・project_title の各キーを含めます。""",
        ),
        (
            "human",
            """メモID: {memo_id}
メモタイトル: {memo_title}
メモステータス: {memo_status}
メモ本文:
{memo_text}

参考タグ: {existing_tags}
現在時刻: {current_datetime_iso}
修正指示（ある場合）: {retry_hint}
JSON のみを返してください。""",
        ),
    ]
)

task_seed_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたはメモから実行可能な単一タスクを抽出するアシスタントです。
メモ本文から直近で着手すべき核心のアクションを見つけ、短いタイトルと任意の補足説明をまとめてください。
タイトルは 60 文字以内、説明は 200 文字以内で簡潔にし、タグは provided_tags の中から適切なものを選んでください。
応答は JSON 形式で title・description・tags を含めます。""",
        ),
        (
            "human",
            """メモID: {memo_id}
メモタイトル: {memo_title}
メモステータス: {memo_status}
メモ本文:
{memo_text}

provided_tags: {existing_tags}
現在時刻: {current_datetime_iso}
修正指示（ある場合）: {retry_hint}
JSON のみで回答してください。""",
        ),
    ]
)

quick_action_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたは GTD の Clarify フェーズで「2分以内タスク」かどうかを判断するアシスタントです。
タスクの手順・準備・所要時間の見積もりを吟味し、短時間で完了できると合理的に判断できる場合のみ
quick action としてください。
判断理由では、必要な作業やコンテキストを踏まえた根拠を一文で提示してください。
応答は JSON 形式で is_quick_action と reason を含めます。""",
        ),
        (
            "human",
            """タスクタイトル: {task_title}
タスク説明: {task_description}
メモID: {memo_id}
メモタイトル: {memo_title}
メモステータス: {memo_status}
メモ全文:
{memo_text}

修正指示（ある場合）: {retry_hint}
JSON のみを返答してください。""",
        ),
    ]
)

responsibility_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたはタスクが自分で実行すべきか、他者へ委譲すべきかを判断するアシスタントです。
タスクの責任範囲、必要な権限、巻き込む相手の情報から、委譲した方が成果やスピード面で優れるかを評価してください。
判断理由では、委譲が適切か否かを決めた要因を簡潔に述べてください。
応答は JSON 形式で should_delegate と reason を含めます。""",
        ),
        (
            "human",
            """タスクタイトル: {task_title}
タスク説明: {task_description}
メモID: {memo_id}
メモタイトル: {memo_title}
メモステータス: {memo_status}
メモ全文:
{memo_text}

修正指示（ある場合）: {retry_hint}
JSON のみで回答してください。""",
        ),
    ]
)

schedule_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたはタスクが特定の日付・時間に紐付くべきかを判断するプランナーです。
締切やイベント依存の要件、依頼内容の緊急度を検討し、具体的な日付が必要かどうかを決めてください。
日付が必要な場合は provided_current_datetime を基準に適切な ISO8601 形式の due_date を提案し、
不要なら null を指定してください。
ISO8601 例: "2025-10-25T10:00:00+09:00"（日時含む）または "2025-10-25"（日付のみ）。
応答は JSON 形式で requires_specific_date・due_date・reason を含めます。""",
        ),
        (
            "human",
            """タスクタイトル: {task_title}
タスク説明: {task_description}
メモID: {memo_id}
メモタイトル: {memo_title}
メモステータス: {memo_status}
メモ全文:
{memo_text}

provided_current_datetime: {current_datetime_iso}
修正指示（ある場合）: {retry_hint}
JSON のみで回答してください。""",
        ),
    ]
)

project_plan_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたはプロジェクト化が妥当なメモから初期プランを作成するアシスタントです。
目標と制約を理解した上で、推奨されるプロジェクト名と、着手順を明確に示す 1〜3 件の次のアクションを
提案してください。
各アクションにはタイトル・任意の説明・必要に応じた期日や優先度・関連タグ・想定作業時間・適切な
Clarify ルートを含め、少なくとも 1 件は next_action に割り当てます。
期日の due_date は ISO8601 形式（例: "2025-10-25T10:00:00+09:00" または "2025-10-25"）、不要なら null。
route は次のいずれかのみ: "next_action" | "progress" | "waiting" | "calendar"。
応答は JSON 形式で project_title と next_actions を含めます。""",
        ),
        (
            "human",
            """メモID: {memo_id}
メモタイトル: {memo_title}
メモステータス: {memo_status}
メモ本文:
{memo_text}

参考タグ: {existing_tags}
現在時刻: {current_datetime_iso}
推奨プロジェクト名の初案: {project_title_hint}
修正指示（ある場合）: {retry_hint}
JSON のみで回答してください。""",
        ),
    ]
)
