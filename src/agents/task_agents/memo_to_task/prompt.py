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
- task: 単一または数ステップで完了可能な具体的行動。長期管理が不要。
- project: 数か月間にわたり作業を要し、継続的に管理が必要。
分類理由は「背景→判断→次の動き」を 120 文字以内で記述し、project の場合は推奨プロジェクト名を
project_title に入れてください。それ以外は null を指定します。
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
        (
            "system",
            """Few-shot 例（正しい出力形）：
    入力: メモタイトル=「週次レポート提出」, 本文=「金曜までに上長へ週次レポートを提出する」
    出力: {{"decision":"task","reason":"具体的な単一行動で外部依存が少ないため","project_title":null}}

        入力: メモタイトル=「新製品サイト構築」, 本文=「新製品のキャンペーンサイトを来月公開する計画を立てる」
        出力: {{"decision":"project","reason":"複数工程・他者協力・継続管理が必要",
            "project_title":"新製品キャンペーンサイト計画"}}

    入力: メモタイトル=「アイディアメモ」, 本文=「将来やってみたいことのメモ」
    出力: {{"decision":"idea","reason":"構想段階で実行手順が未確定","project_title":null}}
    必ず decision と reason と project_title の3キーのみを含む JSON を返してください。""",
        ),
    ]
)

task_seed_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """あなたはメモから実行可能な複数タスクを抽出するプランナーです。
メモ本文を読み、出力粒度に合わせた大きさにタスクを分割してください。
制約:
- 推奨タスク数は {recommended_task_count} 件です（必要に応じて1から10件まで調整可）。{task_count_hint}
- 各タスクの title は 50〜60 文字以内で主体と成果を命令形で記述。
- description は 200 文字以内で完了条件・依存関係・必要リソースを説明（空文字可）。
- due_date は ISO8601 形式の文字列または null（必要時のみ）。
- priority は "low" | "normal" | "high" のいずれか（デフォルトは normal 推奨）。
- tags は provided_tags から 1〜3 個を厳選（該当なしは空配列）。
 - estimate_minutes は 5 の倍数で 15〜240 の整数。
- route は "next_action" | "progress" | "waiting" | "calendar" のいずれか。少なくとも 1 件は next_action を含める。
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
推奨タスク数: {recommended_task_count}
件数調整方針: {task_count_hint}
修正指示（ある場合）: {retry_hint}
JSON のみで回答してください（複数タスクの場合は配列で）。""",
        ),
        (
            "system",
            """Few-shot 例（正しい出力形）：
入力: 本文=「来週のプレゼン準備をする。スライド作成、資料収集、リハーサル」, provided_tags=["仕事","プレゼン"]
出力: {{
    "next_actions": [
        {{"title":"プレゼン資料の要点を整理する","description":"アウトライン作成と必要資料の列挙","due_date":null,"priority":"normal","tags":["仕事"],"estimate_minutes":30,"route":"next_action"}},
        {{"title":"スライドドラフトを作成する","description":"主要スライド10枚の叩き台を作成","due_date":null,"priority":"normal","tags":["仕事","プレゼン"],"estimate_minutes":90,"route":"progress"}},
        {{"title":"リハーサルを実施する","description":"10分の通し練習を1回実施","due_date":"2025-12-14","priority":"high","tags":["プレゼン"],"estimate_minutes":30,"route":"calendar"}}
    ]
}}
ルートは "next_action"|"progress"|"waiting"|"calendar" のみ、due_date は ISO8601 文字列または null です。""",
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
        (
            "system",
            """Few-shot 例（正しい出力形）：
入力: タイトル=「Slackで上長に承認状況を確認する」 説明=「テンプレートメッセージ送信」
    出力: {{"is_quick_action": false, "reason": "外部返信待ちが発生し 2 分を超えるため"}}

入力: タイトル=「机の上の書類をファイルに入れる」
    出力: {{"is_quick_action": true, "reason": "移動なく 2 分以内で完了可能"}}
必ず "is_quick_action" と "reason" のみを含む JSON を返してください。""",
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
        (
            "system",
            """Few-shot 例（正しい出力形）：
入力: タイトル=「法務へ契約レビュー依頼を送る」 説明=「相手がレビューするまで待機」
    出力: {{"should_delegate": true, "reason": "レビュー作業は他者の責務で自身は待機のみ"}}

入力: タイトル=「プレゼン資料の推敲」 説明=「自分の草稿を改善する」
    出力: {{"should_delegate": false, "reason": "自分の成果物の改善で他者への依頼は不要"}}
必ず "should_delegate" と "reason" のみを含む JSON を返してください。""",
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
        (
            "system",
            """Few-shot 例（正しい出力形）：
入力: タイトル=「顧客Aと打合せ」 説明=「来週火曜の午後に訪問」 provided_current_datetime="2025-12-09T10:00:00+09:00"
    出力: {{"requires_specific_date": true, "due_date": "2025-12-16T15:00:00+09:00", "reason": "明示的に日時指定あり"}}

入力: タイトル=「社内Wikiの整備」 説明=「空いている時間で進める」
    出力: {{"requires_specific_date": false, "due_date": null, "reason": "外部要因やイベント指定がないため"}}
必ず "requires_specific_date" と "due_date" と "reason" のみを含む JSON を返してください。""",
        ),
    ]
)
