"""Add i18n support for users, organizations, and courses

Revision ID: i18n_001
Revises: eb10d15465b3
Create Date: 2025-11-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'i18n_001'
down_revision: Union[str, None] = 'eb10d15465b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add preferred_locale to user table
    op.add_column('user', sa.Column('preferred_locale', sa.String(length=5), nullable=True, server_default='en'))

    # Add default_locale and supported_locales to organization table
    op.add_column('organization', sa.Column('default_locale', sa.String(length=5), nullable=True, server_default='en'))
    op.add_column('organization', sa.Column('supported_locales', sa.JSON(), nullable=True, server_default='["en"]'))

    # Add translations JSON field to course table
    op.add_column('course', sa.Column('translations', sa.JSON(), nullable=True, server_default='{}'))

    # Add translations JSON field to chapter table
    op.add_column('chapter', sa.Column('translations', sa.JSON(), nullable=True, server_default='{}'))

    # Add translations JSON field to activity table
    op.add_column('activity', sa.Column('translations', sa.JSON(), nullable=True, server_default='{}'))


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column('activity', 'translations')
    op.drop_column('chapter', 'translations')
    op.drop_column('course', 'translations')
    op.drop_column('organization', 'supported_locales')
    op.drop_column('organization', 'default_locale')
    op.drop_column('user', 'preferred_locale')
