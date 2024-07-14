"""empty message

Revision ID: bb5da1e68550
Revises: 8ca023a4a4b0
Create Date: 2022-08-29 13:06:57.697368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bb5da1e68550"
down_revision = "8ca023a4a4b0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "items",
        "price",
        existing_type=sa.REAL(),
        type_=sa.Float(precision=2),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "password",
        existing_type=sa.VARCHAR(length=80),
        type_=sa.String(length=256),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users",
        "password",
        existing_type=sa.String(length=256),
        type_=sa.VARCHAR(length=80),
        existing_nullable=False,
    )
    op.alter_column(
        "items",
        "price",
        existing_type=sa.Float(precision=2),
        type_=sa.REAL(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
