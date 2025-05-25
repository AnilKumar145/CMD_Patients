"""create patients table

Revision ID: 7c85a2ef810b
Revises: 
Create Date: 2025-03-05 16:33:23.850804

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7c85a2ef810b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create patients table using the existing gender enum
    op.create_table('patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=15), nullable=False),
        sa.Column('gender', sa.String(length=10), nullable=False),  # Changed to String instead of ENUM
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=10), nullable=False, server_default='ACTIVE'),
        sa.Column('street', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=50), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('country', sa.String(length=50), nullable=False),
        sa.Column('postal_code', sa.String(length=10), nullable=False),
        sa.Column('profile_image', sa.LargeBinary(), nullable=True),
        sa.Column('medical_history', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('patient_id'),
        sa.CheckConstraint("gender IN ('MALE', 'FEMALE', 'OTHERS')", name='valid_gender')
    )


def downgrade():
    op.drop_table('patients')
