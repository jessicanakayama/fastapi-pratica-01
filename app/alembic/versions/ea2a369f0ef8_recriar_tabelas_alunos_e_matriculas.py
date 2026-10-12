
"""Recriar tabelas alunos e matriculas

Revision ID: ea2a369f0ef8
Revises: 1cf34ecaf334
"""

from alembic import op
import sqlalchemy as sa


revision = "ea2a369f0ef8"
down_revision = "1cf34ecaf334"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alunos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("turma", sa.Integer(), nullable=False),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("alterado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["curso_id"], ["cursos.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_alunos_id", "alunos", ["id"], unique=False)

    op.create_table(
        "matriculas",
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("disciplina_id", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["aluno_id"], ["alunos.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["disciplina_id"], ["disciplinas.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("aluno_id", "disciplina_id"),
    )


def downgrade() -> None:
    op.drop_table("matriculas")
    op.drop_index("ix_alunos_id", table_name="alunos")
    op.drop_table("alunos")
