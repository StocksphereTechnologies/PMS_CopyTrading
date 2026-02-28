"""Initial schema with automated login

Revision ID: 4fbb45908ac7
Revises: 
Create Date: 2026-01-14 01:35:43.339529

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '4fbb45908ac7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True, server_default='India'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], unique=False)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=False)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)

    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('account_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('broker_name', sa.String(length=50), nullable=False),
        sa.Column('nickname', sa.String(length=100), nullable=True),
        sa.Column('trading_login_id', sa.String(length=255), nullable=False),
        sa.Column('encrypted_password', sa.Text(), nullable=True),
        sa.Column('encrypted_totp_secret', sa.Text(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('encrypted_login_password', sa.Text(), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('api_secret', sa.Text(), nullable=True),
        sa.Column('user_key', sa.String(length=255), nullable=True),
        sa.Column('app_source', sa.String(length=255), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('token_generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_validated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('subscription_type', sa.String(length=20), nullable=True),
        sa.Column('subscription_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('subscription_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('account_id')
    )
    op.create_index(op.f('ix_accounts_account_id'), 'accounts', ['account_id'], unique=False)
    op.create_index(op.f('ix_accounts_broker_name'), 'accounts', ['broker_name'], unique=False)
    op.create_index(op.f('ix_accounts_is_enabled'), 'accounts', ['is_enabled'], unique=False)
    op.create_index(op.f('ix_accounts_is_paid'), 'accounts', ['is_paid'], unique=False)
    op.create_index(op.f('ix_accounts_is_validated'), 'accounts', ['is_validated'], unique=False)
    op.create_index(op.f('ix_accounts_owner_id'), 'accounts', ['owner_id'], unique=False)

    # Create trades table
    op.create_table(
        'trades',
        sa.Column('trade_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(length=100), nullable=False),
        sa.Column('exchange', sa.String(length=50), nullable=False),
        sa.Column('side', sa.Enum('BUY', 'SELL', name='orderside'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('order_type', sa.Enum('MARKET', 'LIMIT', 'SL', 'SL_M', name='ordertype'), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('trade_id')
    )
    op.create_index(op.f('ix_trades_created_at'), 'trades', ['created_at'], unique=False)
    op.create_index(op.f('ix_trades_owner_id'), 'trades', ['owner_id'], unique=False)
    op.create_index(op.f('ix_trades_symbol'), 'trades', ['symbol'], unique=False)
    op.create_index(op.f('ix_trades_trade_id'), 'trades', ['trade_id'], unique=False)

    # Create trade_executions table
    op.create_table(
        'trade_executions',
        sa.Column('execution_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('trade_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('broker', sa.String(length=50), nullable=False),
        sa.Column('order_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', 'PARTIAL', 'CANCELLED', name='orderstatus'), nullable=False, server_default='PENDING'),
        sa.Column('executed_price', sa.Float(), nullable=True),
        sa.Column('executed_quantity', sa.Integer(), nullable=True),
        sa.Column('error_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.account_id'], ),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.trade_id'], ),
        sa.PrimaryKeyConstraint('execution_id')
    )
    op.create_index(op.f('ix_trade_executions_account_id'), 'trade_executions', ['account_id'], unique=False)
    op.create_index(op.f('ix_trade_executions_execution_id'), 'trade_executions', ['execution_id'], unique=False)
    op.create_index(op.f('ix_trade_executions_trade_id'), 'trade_executions', ['trade_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_trade_executions_trade_id'), table_name='trade_executions')
    op.drop_index(op.f('ix_trade_executions_execution_id'), table_name='trade_executions')
    op.drop_index(op.f('ix_trade_executions_account_id'), table_name='trade_executions')
    op.drop_table('trade_executions')
    
    op.drop_index(op.f('ix_trades_trade_id'), table_name='trades')
    op.drop_index(op.f('ix_trades_symbol'), table_name='trades')
    op.drop_index(op.f('ix_trades_owner_id'), table_name='trades')
    op.drop_index(op.f('ix_trades_created_at'), table_name='trades')
    op.drop_table('trades')
    
    op.drop_index(op.f('ix_accounts_owner_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_is_validated'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_is_paid'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_is_enabled'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_broker_name'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_account_id'), table_name='accounts')
    op.drop_table('accounts')
    
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
