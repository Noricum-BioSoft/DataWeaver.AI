"""Add biological entities tables

Revision ID: 002
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create designs table
    op.create_table('designs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('alias', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence', sa.Text(), nullable=False),
        sa.Column('sequence_type', sa.String(length=50), nullable=False),
        sa.Column('mutation_list', sa.Text(), nullable=True),
        sa.Column('parent_design_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('lineage_hash', sa.String(length=64), nullable=False),
        sa.Column('generation', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['parent_design_id'], ['designs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_designs_alias'), 'designs', ['alias'], unique=False)
    op.create_index(op.f('ix_designs_lineage_hash'), 'designs', ['lineage_hash'], unique=False)
    op.create_index(op.f('ix_designs_name'), 'designs', ['name'], unique=False)
    op.create_index(op.f('ix_designs_sequence'), 'designs', ['sequence'], unique=False)

    # Create builds table
    op.create_table('builds',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('alias', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence', sa.Text(), nullable=False),
        sa.Column('sequence_type', sa.String(length=50), nullable=False),
        sa.Column('mutation_list', sa.Text(), nullable=True),
        sa.Column('parent_build_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('design_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lineage_hash', sa.String(length=64), nullable=False),
        sa.Column('generation', sa.Integer(), nullable=True),
        sa.Column('construct_type', sa.String(length=100), nullable=True),
        sa.Column('build_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['design_id'], ['designs.id'], ),
        sa.ForeignKeyConstraint(['parent_build_id'], ['builds.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_builds_alias'), 'builds', ['alias'], unique=False)
    op.create_index(op.f('ix_builds_lineage_hash'), 'builds', ['lineage_hash'], unique=False)
    op.create_index(op.f('ix_builds_name'), 'builds', ['name'], unique=False)
    op.create_index(op.f('ix_builds_sequence'), 'builds', ['sequence'], unique=False)

    # Create tests table
    op.create_table('tests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('alias', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('test_type', sa.String(length=100), nullable=False),
        sa.Column('assay_name', sa.String(length=255), nullable=True),
        sa.Column('protocol', sa.String(length=255), nullable=True),
        sa.Column('result_value', sa.Float(), nullable=True),
        sa.Column('result_unit', sa.String(length=50), nullable=True),
        sa.Column('result_type', sa.String(length=50), nullable=True),
        sa.Column('match_confidence', sa.String(length=20), nullable=True),
        sa.Column('match_method', sa.String(length=100), nullable=True),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('design_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('build_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('test_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('technician', sa.String(length=255), nullable=True),
        sa.Column('lab_conditions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['build_id'], ['builds.id'], ),
        sa.ForeignKeyConstraint(['design_id'], ['designs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tests_alias'), 'tests', ['alias'], unique=False)
    op.create_index(op.f('ix_tests_name'), 'tests', ['name'], unique=False)

    # Create additional indexes for performance
    op.create_index('idx_designs_sequence', 'designs', ['sequence'], unique=False)
    op.create_index('idx_designs_lineage_hash', 'designs', ['lineage_hash'], unique=False)
    op.create_index('idx_builds_sequence', 'builds', ['sequence'], unique=False)
    op.create_index('idx_builds_lineage_hash', 'builds', ['lineage_hash'], unique=False)
    op.create_index('idx_tests_design_id', 'tests', ['design_id'], unique=False)
    op.create_index('idx_tests_build_id', 'tests', ['build_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('idx_tests_build_id', table_name='tests')
    op.drop_index('idx_tests_design_id', table_name='tests')
    op.drop_index('idx_builds_lineage_hash', table_name='builds')
    op.drop_index('idx_builds_sequence', table_name='builds')
    op.drop_index('idx_designs_lineage_hash', table_name='designs')
    op.drop_index('idx_designs_sequence', table_name='designs')

    # Drop tables
    op.drop_index(op.f('ix_tests_name'), table_name='tests')
    op.drop_index(op.f('ix_tests_alias'), table_name='tests')
    op.drop_table('tests')
    
    op.drop_index(op.f('ix_builds_sequence'), table_name='builds')
    op.drop_index(op.f('ix_builds_name'), table_name='builds')
    op.drop_index(op.f('ix_builds_lineage_hash'), table_name='builds')
    op.drop_index(op.f('ix_builds_alias'), table_name='builds')
    op.drop_table('builds')
    
    op.drop_index(op.f('ix_designs_sequence'), table_name='designs')
    op.drop_index(op.f('ix_designs_name'), table_name='designs')
    op.drop_index(op.f('ix_designs_lineage_hash'), table_name='designs')
    op.drop_index(op.f('ix_designs_alias'), table_name='designs')
    op.drop_table('designs') 