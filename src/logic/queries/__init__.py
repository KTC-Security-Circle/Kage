"""Query DTOs for Application Service layer

このパッケージは、Application Service層で使用するQuery DTOsを提供します。
"""

from logic.queries.memo_queries import (
    GetAllMemosQuery,
    GetMemoByIdQuery,
    GetMemosByTaskIdQuery,
    SearchMemosQuery,
)
from logic.queries.one_liner_queries import OneLinerContext
from logic.queries.project_queries import (
    GetActiveProjectsQuery,
    GetAllProjectsQuery,
    GetCompletedProjectsQuery,
    GetProjectByIdQuery,
    GetProjectsByStatusQuery,
    SearchProjectsByTitleQuery,
)
from logic.queries.tag_queries import (
    CheckTagExistsByNameQuery,
    GetAllTagsQuery,
    GetTagByIdQuery,
    GetTagByNameQuery,
    SearchTagsByNameQuery,
)
from logic.queries.task_queries import (
    GetAllTasksByStatusDictQuery,
    GetTaskByIdQuery,
    GetTasksByStatusQuery,
    GetTodayTasksCountQuery,
)
from logic.queries.task_tag_queries import (
    CheckTaskTagExistsQuery,
    GetAllTaskTagsQuery,
    GetTaskTagByTaskAndTagQuery,
    GetTaskTagsByTagIdQuery,
    GetTaskTagsByTaskIdQuery,
)

__all__ = [
    # Memo Queries
    "GetAllMemosQuery",
    "GetMemoByIdQuery",
    "GetMemosByTaskIdQuery",
    "SearchMemosQuery",
    # One-liner Queries
    "OneLinerContext",
    # Project Queries
    "GetActiveProjectsQuery",
    "GetAllProjectsQuery",
    "GetCompletedProjectsQuery",
    "GetProjectByIdQuery",
    "GetProjectsByStatusQuery",
    "SearchProjectsByTitleQuery",
    # Tag Queries
    "CheckTagExistsByNameQuery",
    "GetAllTagsQuery",
    "GetTagByIdQuery",
    "GetTagByNameQuery",
    "SearchTagsByNameQuery",
    # Task Queries
    "GetAllTasksByStatusDictQuery",
    "GetTaskByIdQuery",
    "GetTasksByStatusQuery",
    "GetTodayTasksCountQuery",
    # TaskTag Queries
    "CheckTaskTagExistsQuery",
    "GetAllTaskTagsQuery",
    "GetTaskTagByTaskAndTagQuery",
    "GetTaskTagsByTagIdQuery",
    "GetTaskTagsByTaskIdQuery",
]
