from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_catalogue"
down_revision = "0002_ledger"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cms_catalogue_versions", sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("cms_catalogue_versions", sa.Column("import_status", sa.String(length=32), nullable=False, server_default="complete"))
    op.add_column("cms_catalogue_versions", sa.Column("parser_version", sa.String(length=64), nullable=True))
    op.add_column("cms_catalogue_versions", sa.Column("note", sa.Text(), nullable=True))
    op.create_unique_constraint("uq_cms_catalogue_versions_source_hash", "cms_catalogue_versions", ["source_hash"])
    op.add_column("cms_catalogue_items", sa.Column("source_row_no", sa.Integer(), nullable=True))
    op.create_check_constraint("ck_cms_catalogue_versions_row_count_nonnegative", "cms_catalogue_versions", "row_count >= 0")


def downgrade() -> None:
    op.drop_constraint("ck_cms_catalogue_versions_row_count_nonnegative", "cms_catalogue_versions", type_="check")
    op.drop_column("cms_catalogue_items", "source_row_no")
    op.drop_constraint("uq_cms_catalogue_versions_source_hash", "cms_catalogue_versions", type_="unique")
    op.drop_column("cms_catalogue_versions", "note")
    op.drop_column("cms_catalogue_versions", "parser_version")
    op.drop_column("cms_catalogue_versions", "import_status")
    op.drop_column("cms_catalogue_versions", "row_count")
