from sqlalchemy import Column, String
from alembic import op

def upgrade():
    # Add message_link column to message_groups table
    op.add_column('message_groups', Column('message_link', String))

def downgrade():
    # Remove message_link column from message_groups table
    op.drop_column('message_groups', 'message_link')
