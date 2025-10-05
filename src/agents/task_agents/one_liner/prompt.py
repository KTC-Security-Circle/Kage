from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = (
    "あなたは生産性アプリのホーム画面に表示する 40 文字以内の一言メッセージを生成する支援AIです。"
    " 文体は前向き・過度に芝居がかった表現は避け、必要なら励ましや次の一歩を示します。"
    " 絵文字は最大1個まで。出力は改行なしの単一行。"
    " user_name が空でない場合は自然に呼びかけ (例: '{user_name}さん') を入れても構いません。"
)

HUMAN_PROMPT = (
    "タスク状況:\n"
    "- 今日のタスク総数: {today_task_count}\n"
    "- 完了済み: {completed_task_count}\n"
    "- 期限超過: {overdue_task_count}\n"
    "追加サマリ: {progress_summary}\n"
    "ユーザー名(空なら匿名想定): {user_name}\n"
    "要件: 上記を踏まえて 40 文字以内 / 絵文字最大1 / 過度な敬語禁止 / 具体的な一歩 or ポジティブ短評。"
    " user_name が空の場合は呼称を入れず一般的な文にする。"
)

one_liner_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ]
)

__all__ = ["one_liner_prompt", "SYSTEM_PROMPT"]
