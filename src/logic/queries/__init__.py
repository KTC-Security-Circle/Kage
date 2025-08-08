"""Query DTOs for Application Service layer

このパッケージは、Application Service層で使用するQuery DTOsを提供します。
"""

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
