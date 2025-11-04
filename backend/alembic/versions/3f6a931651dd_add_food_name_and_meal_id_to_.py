"""add_food_name_and_meal_id_to_nutritional_logs

Revision ID: 3f6a931651dd
Revises: 8171d8e12f44
Create Date: 2025-11-03 09:58:11.298592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f6a931651dd'
down_revision: Union[str, None] = '8171d8e12f44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add food_name column to nutritional_logs table
    op.add_column('nutritional_logs', sa.Column('food_name', sa.String(), nullable=True))
    
    # Add meal_id column to nutritional_logs table
    op.add_column('nutritional_logs', sa.Column('meal_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint for meal_id
    op.create_foreign_key(
        'fk_nutritional_logs_meal_id',
        'nutritional_logs',
        'meal_plan_meals',
        ['meal_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Add index on meal_id for better query performance
    op.create_index('ix_nutritional_logs_meal_id', 'nutritional_logs', ['meal_id'])


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_nutritional_logs_meal_id', 'nutritional_logs')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_nutritional_logs_meal_id', 'nutritional_logs', type_='foreignkey')
    
    # Drop columns
    op.drop_column('nutritional_logs', 'meal_id')
    op.drop_column('nutritional_logs', 'food_name')
