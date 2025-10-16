"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=True),
        sa.Column('two_factor_secret', sa.String(), nullable=True),
        sa.Column('oauth_provider', sa.String(), nullable=True),
        sa.Column('oauth_id', sa.String(), nullable=True),
        sa.Column('profile_picture', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create health_profiles table
    op.create_table(
        'health_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('occupation_type', sa.String(), nullable=True),
        sa.Column('activity_level', sa.String(), nullable=True),
        sa.Column('fitness_goal', sa.String(), nullable=True),
        sa.Column('target_weight', sa.Float(), nullable=True),
        sa.Column('target_activity_level', sa.String(), nullable=True),
        sa.Column('preferred_exercise_time', sa.String(), nullable=True),
        sa.Column('preferred_exercise_environment', sa.String(), nullable=True),
        sa.Column('weekly_activity_frequency', sa.Integer(), nullable=True),
        sa.Column('exercise_types', sa.String(), nullable=True),
        sa.Column('average_session_duration', sa.String(), nullable=True),
        sa.Column('fitness_level', sa.String(), nullable=True),
        sa.Column('endurance_level', sa.Integer(), nullable=True),
        sa.Column('strength_indicators', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_profiles_id'), 'health_profiles', ['id'], unique=False)

    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('activity_type', sa.String(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('intensity', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'], unique=False)

    # Create metrics_history table
    op.create_table(
        'metrics_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('health_profile_id', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('bmi', sa.Float(), nullable=True),
        sa.Column('wellness_score', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['health_profile_id'], ['health_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metrics_history_id'), 'metrics_history', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_metrics_history_id'), table_name='metrics_history')
    op.drop_table('metrics_history')
    
    op.drop_index(op.f('ix_activity_logs_id'), table_name='activity_logs')
    op.drop_table('activity_logs')
    
    op.drop_index(op.f('ix_health_profiles_id'), table_name='health_profiles')
    op.drop_table('health_profiles')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users') 