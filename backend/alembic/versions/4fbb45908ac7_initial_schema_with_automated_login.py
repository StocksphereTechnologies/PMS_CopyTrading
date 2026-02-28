"""Neutralized redundant migration
Alembic had multiple heads, so this file merges them into a single path.
"""
revision = 'head_merge_fix'
down_revision = '4fbb45908ac7'
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
