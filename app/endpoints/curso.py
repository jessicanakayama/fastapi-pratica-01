from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.curso import Curso
from app.schemas import CursoCreate, CursoResponse
from app.core import requer_coordenador, requer_professor_ou_coordenador

# Roteador com o prefixo e a tag para organizar o Swagger
router = APIRouter(
    prefix="/cursos",
    tags=["Cursos"]
)

# APENAS COORDENADORES podem criar cursos
# 1. CRIAR CURSO (POST /cursos)
@router.post("", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def criar_curso(
    curso_dados: CursoCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_coordenador)
):
    novo_curso = Curso(
        nome=curso_dados.nome,
        duracao=curso_dados.duracao
    )
    db.add(novo_curso)
    await db.commit()

    statement = (
        select(Curso)
        .options(
            selectinload(Curso.disciplina),
            selectinload(Curso.aluno)
        )
        .where(Curso.id == novo_curso.id)
    )
    result = await db.execute(statement)
    return result.scalar_one()


# PROFESSORES E COORDENADORES podem listar cursos
# 2. LISTAR TODOS OS CURSOS (GET /cursos)
@router.get("", response_model=List[CursoResponse])
async def listar_cursos(
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor_ou_coordenador)
):
    statement = select(Curso).options(
        selectinload(Curso.disciplina),
        selectinload(Curso.aluno)
    )
    result = await db.execute(statement)
    return result.scalars().all()


# PROFESSORES E COORDENADORES podem buscar cursos
# 3. BUSCAR UM CURSO POR ID (GET /cursos/{curso_id})
@router.get("/{curso_id}", response_model=CursoResponse)
async def buscar_curso(
    curso_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor_ou_coordenador)
):
    statement = (
        select(Curso)
        .options(
            selectinload(Curso.disciplina),
            selectinload(Curso.aluno)
        )
        .where(Curso.id == curso_id)
    )
    result = await db.execute(statement)
    curso = result.scalar_one_or_none()

    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso não encontrado"
        )

    return curso


# APENAS COORDENADORES podem alterar cursos
# 4. ATUALIZAR UM CURSO (PUT /cursos/{curso_id})
@router.put("/{curso_id}", response_model=CursoResponse)
async def atualizar_curso(
    curso_id: int,
    curso_dados: CursoCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_coordenador)
):
    result = await db.execute(
        select(Curso).where(Curso.id == curso_id)
    )
    curso = result.scalar_one_or_none()

    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso não encontrado"
        )

    curso.nome = curso_dados.nome
    curso.duracao = curso_dados.duracao
    await db.commit()

    statement = (
        select(Curso)
        .options(
            selectinload(Curso.disciplina),
            selectinload(Curso.aluno)
        )
        .where(Curso.id == curso_id)
    )
    result = await db.execute(statement)
    return result.scalar_one()


# APENAS COORDENADORES podem deletar cursos
# 5. DELETAR UM CURSO (DELETE /cursos/{curso_id})
@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_curso(
    curso_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_coordenador)
):
    result = await db.execute(
        select(Curso).where(Curso.id == curso_id)
    )
    curso = result.scalar_one_or_none()

    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curso não encontrado"
        )

    await db.delete(curso)
    await db.commit()
    return None