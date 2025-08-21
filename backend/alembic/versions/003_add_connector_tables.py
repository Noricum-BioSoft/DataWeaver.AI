"""Add connector tables

Revision ID: 003
Revises: 002_add_bio_entities
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_add_bio_entities'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
            op.execute("CREATE TYPE connectortype AS ENUM ('GOOGLE_WORKSPACE', 'MICROSOFT_365', 'SLACK', 'EMAIL', 'DATABASE', 'API', 'FILE_SYSTEM', 'LIMS', 'OMICS', 'LITERATURE', 'CLINICAL')")
        op.execute("CREATE TYPE connectorstatus AS ENUM ('disconnected', 'connecting', 'connected', 'error', 'syncing')")
        op.execute("CREATE TYPE authenticationtype AS ENUM ('OAUTH2', 'API_KEY', 'USERNAME_PASSWORD', 'TOKEN', 'NONE')")
    
    # Create connectors table
    op.create_table('connectors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('connector_type', sa.Enum('google_workspace', 'microsoft_365', 'slack', 'email', 'database', 'api', 'file_system', 'lims', 'omics', 'literature', 'clinical', name='connectortype'), nullable=False),
        sa.Column('status', sa.Enum('disconnected', 'connecting', 'connected', 'error', 'syncing', name='connectorstatus'), nullable=True),
        sa.Column('auth_type', sa.Enum('oauth2', 'api_key', 'username_password', 'token', 'none', name='authenticationtype'), nullable=False),
        sa.Column('auth_config', sa.JSON(), nullable=True),
        sa.Column('connection_config', sa.JSON(), nullable=True),
        sa.Column('sync_enabled', sa.Boolean(), nullable=True),
        sa.Column('sync_schedule', sa.String(length=100), nullable=True),
        sa.Column('last_sync', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_sync', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_connectors_id'), 'connectors', ['id'], unique=False)
    
    # Create data_sources table
    op.create_table('data_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('connector_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(length=100), nullable=True),
        sa.Column('source_path', sa.String(length=500), nullable=True),
        sa.Column('schema', sa.JSON(), nullable=True),
        sa.Column('source_metadata', sa.JSON(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('sync_enabled', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['connector_id'], ['connectors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_sources_id'), 'data_sources', ['id'], unique=False)
    
    # Create data_extracts table
    op.create_table('data_extracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_source_id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=True),
        sa.Column('extract_type', sa.String(length=100), nullable=True),
        sa.Column('extract_config', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('data_file_path', sa.String(length=500), nullable=True),
        sa.Column('data_format', sa.String(length=50), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True),
        sa.Column('column_count', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['data_source_id'], ['data_sources.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_extracts_id'), 'data_extracts', ['id'], unique=False)
    
    # Create connector_sync_logs table
    op.create_table('connector_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('connector_id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=True),
        sa.Column('records_added', sa.Integer(), nullable=True),
        sa.Column('records_updated', sa.Integer(), nullable=True),
        sa.Column('records_deleted', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['connector_id'], ['connectors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_connector_sync_logs_id'), 'connector_sync_logs', ['id'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_connector_sync_logs_id'), table_name='connector_sync_logs')
    op.drop_table('connector_sync_logs')
    
    op.drop_index(op.f('ix_data_extracts_id'), table_name='data_extracts')
    op.drop_table('data_extracts')
    
    op.drop_index(op.f('ix_data_sources_id'), table_name='data_sources')
    op.drop_table('data_sources')
    
    op.drop_index(op.f('ix_connectors_id'), table_name='connectors')
    op.drop_table('connectors')
    
    # Drop enum types
    op.execute("DROP TYPE authenticationtype")
    op.execute("DROP TYPE connectorstatus")
    op.execute("DROP TYPE connectortype")
