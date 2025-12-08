"""メモ→タスク変換エージェント用プロンプト定義。"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

classification_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたは GTD の Clarify/Organize フェーズを支援するアナリストです。
以下の定義に従ってメモを判別し、最も適切なカテゴリを一つだけ返してください。
- idea: 調査や構想レベルで、まだ具体的な実行手順が定まっていない。
- task: 単一または数ステップで完了可能な具体的行動。外部依存や長期管理が不要。
- project: 数か月間にわたり複数ステップを要し他者協力や外部リソースが必要な場合や、継続的に管理が必要。
分類理由は「背景→判断→次の動き」を 120 文字以内で記述し、project の場合は推奨プロジェクト名を
project_title に入れてください。それ以外は null を指定します。
必ず次の JSON スキーマで出力します: {{"reason":"...","decision":"idea|task|project","project_title":string|null}}。
出力粒度ヒント: {detail_hint}
追加指示:
{custom_instructions}
""",
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
            """あなたはメモから最優先の単一タスクを抽出するアシスタントです。
メモ本文を読み、直近 1 手の行動を 1 つだけ選び、結果が観測可能なタイトル・補足説明・タグにまとめます。
制約: title は 60 文字以内で命令形、description は 200 文字以内で完了条件と必要リソースを説明します。
tags は provided_tags から 1〜3 個を厳選してください（該当なしの場合は空配列）。
必ず次の JSON を返します: {{"title":string,"description":string,"tags":list[str]}}。
出力粒度ヒント: {detail_hint}
追加指示:
{custom_instructions}
""",
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
            """あなたは GTD Clarify フェーズで「2 分以内タスク」かを検証するアシスタントです。
準備物の取得・移動時間・外部待ち時間を含め、実行に 2 分を超える要素がある場合は quick action に
してはいけません。判断では「時間見積もり」「阻害要因」を必ず確認してください。
理由は 1 文で、どの作業が制約になったかを具体的に書きます。
JSON 形式: {{"reason":string,"is_quick_action":true|false}}。
出力粒度ヒント: {detail_hint}
追加指示:
{custom_instructions}
""",
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
            """あなたはタスクを自分で担うか、他者へ委譲するかを決めるエージェントです。
判断指針:
1. メモの中に他者へ依頼する旨の指示があるか。
2. 自身でやるべきものではないという旨の示唆があるか。
作業者に自身を含みそうな場合は should_delegate を false にしてください。
他人に完全に委譲し自身はただ待つだけのタスクのみ should_delegate を true にします。
理由文では、判断に寄与した資源・スキル・依存関係を 100 文字以内で説明してください。
JSON 形式: {{"reason":string,"should_delegate":true|false}}。
出力粒度ヒント: {detail_hint}
追加指示:
{custom_instructions}
""",
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
            """あなたはタスクに日時が必要かを判断するプランナーです。
以下を網羅的に確認してください。
1. 明示的な締切・イベントや他者の期待日があるか。
2. 実行タイミングが外部要因（会場・天候・営業時間）に縛られているか。
3. 依存ステップや準備期間から逆算が必要か。
もし明確な日付や時間、曜日などがわかる場合は due_date に provided_current_datetime から計算した時間を
ISO8601 文字列で提案してください。
reason には日付を付ける根拠または不要な理由を 120 文字以内で記述します。
JSON 形式: {{"reason":string,"requires_specific_date":true|false,"due_date":string|null}}。
出力粒度ヒント: {detail_hint}
追加指示:
{custom_instructions}
""",
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
            """あなたはプロジェクト化されたメモから最初の実行プランを作るプランナーです。
目的と制約を要約し、以下を厳密に出力してください。
1. project_title: 40 文字以内で成果が一目でわかる名称。
2. next_actions: 推奨は {recommended_task_count} 件です（必要に応じて調整可）。{task_count_hint}
   各要素は {{"title", "description", "due_date", "priority", "tags", "estimated_minutes", "route"}}
   を含めます。
- title: 50 文字以内で主体と成果を記述。
- description: 200 文字以内で完了条件や依存関係を補足（空文字可）。
- due_date: ISO8601 形式または null。
- priority: "low" | "normal" | "high" のいずれか。
- tags: provided existing_tags から 1〜3 個選択。
- estimated_minutes: 5 の倍数で 15〜240 の整数。
- route: "next_action" | "progress" | "waiting" | "calendar" のいずれかで、少なくとも 1 件は next_action を指定。
JSON ブロック以外は出力しません。
出力粒度ヒント: {detail_hint}
追加指示:
{custom_instructions}
""",
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
