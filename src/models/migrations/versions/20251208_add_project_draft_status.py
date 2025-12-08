"""add project draft status

Revision ID: 20251208_add_project_draft_status
Revises: 8ba1209fe648
Create Date: 2025-12-08 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20251208_add_project_draft_status"
down_revision: Union[str, Sequence[str], None] = "8ba1209fe648"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    bind = op.get_bind()
    return bind.dialect.name == "sqlite"


def upgrade() -> None:
    if _is_sqlite():
        # SQLite は TEXT で enum を表現しているため、追加作業は不要。
        return

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectstatus') THEN
                CREATE TYPE projectstatus AS ENUM ('DRAFT', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED');
            ELSIF NOT EXISTS (
                SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid
                WHERE t.typname = 'projectstatus' AND e.enumlabel = 'DRAFT'
            ) THEN
                ALTER TYPE projectstatus ADD VALUE 'DRAFT' BEFORE 'ACTIVE';
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    if _is_sqlite():
        return

    conn = op.get_bind()
    has_type = conn.execute("SELECT 1 FROM pg_type WHERE typname = 'projectstatus'").scalar()
    if not has_type:
        return
    op.execute("ALTER TYPE projectstatus RENAME TO projectstatus_old")
    op.execute("CREATE TYPE projectstatus AS ENUM ('ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED')")
    op.execute(
        """
        ALTER TABLE projects
        ALTER COLUMN status TYPE projectstatus
        USING CASE
            WHEN status = 'DRAFT' THEN 'ACTIVE'::projectstatus
            ELSE status::text::projectstatus
        END
        """
    )
    op.execute("DROP TYPE projectstatus_old")
