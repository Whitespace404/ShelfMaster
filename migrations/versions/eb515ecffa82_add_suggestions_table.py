"""Add Suggestions table

Revision ID: eb515ecffa82
Revises: d7cd4f635555
Create Date: 2023-11-18 22:36:23.668332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb515ecffa82'
down_revision = 'd7cd4f635555'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('suggestions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('book_name', sa.String(length=80), nullable=True),
    sa.Column('author_name', sa.String(length=80), nullable=True),
    sa.Column('submit_reason', sa.String(length=120), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('suggestions')
    # ### end Alembic commands ###
