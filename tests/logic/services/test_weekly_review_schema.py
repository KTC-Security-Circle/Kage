"""WeeklyReviewInsights モデルのスキーマ検証。"""

from models import WeeklyReviewInsights


def test_weekly_review_insights_schema_contains_sections() -> None:
    schema = WeeklyReviewInsights.model_json_schema()

    assert "metadata" in schema["properties"]
    assert "highlights" in schema["properties"]
    assert "zombie_tasks" in schema["properties"]
    assert "memo_audits" in schema["properties"]
