from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.aluno import Aluno
from app.models.disciplina import Disciplina
from app.models.matricula import Matricula
from app.schemas import MatriculaCreate, MatriculaResponse
from app.core import requer_coordenador, requer_professor_ou_coordenador

router = APIRouter(
    prefix="/matriculas",
    tags=["Matriculas"]
)


# 1. CRIAR MATRÍCULA (POST /matriculas)
# Apenas coordenadores podem criar
@router.post("", response_model=MatriculaResponse, status_code=status.HTTP_201_CREATED)
async def criar_matricula(
    dados: MatriculaCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_coordenador)
):
    result_aluno = await db.execute(
        select(Aluno).where(Aluno.id == dados.aluno_id)
    )
    aluno_existe = result_aluno.scalar_one_or_none()

    if not aluno_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível efetuar a matrícula. O aluno com ID {dados.aluno_id} não existe."
        )

    result_disc = await db.execute(
        select(Disciplina).where(Disciplina.id == dados.disciplina_id)
    )
    disciplina_existe = result_disc.scalar_one_or_none()

    if not disciplina_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível efetuar a matrícula. A disciplina com ID {dados.disciplina_id} não existe."
        )

    nova_matricula = Matricula(
        aluno_id=dados.aluno_id,
        disciplina_id=dados.disciplina_id
    )

    db.add(nova_matricula)
    await db.commit()

    statement = (
        select(Matricula)
        .options(
            selectinload(Matricula.aluno),
            selectinload(Matricula.disciplina)
        )
        .where(
            Matricula.aluno_id == nova_matricula.aluno_id,
            Matricula.disciplina_id == nova_matricula.disciplina_id
        )
    )

    result = await db.execute(statement)
    return result.scalar_one()


# 2. LISTAR TODAS AS MATRÍCULAS (GET /matriculas)
# Professores e coordenadores podem listar
@router.get("", response_model=List[MatriculaResponse])
async def listar_matriculas(
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor_ou_coordenador)
):
    statement = select(Matricula).options(
        selectinload(Matricula.aluno),
        selectinload(Matricula.disciplina)
    )

    result = await db.execute(statement)
    return result.scalars().all()


# 3. BUSCAR MATRÍCULA (GET /matriculas/{aluno_id}/{disciplina_id})
# Professores e coordenadores podem buscar
@router.get("/{aluno_id}/{disciplina_id}", response_model=MatriculaResponse)
async def buscar_matricula(
    aluno_id: int,
    disciplina_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor_ou_coordenador)
):
    statement = (
        select(Matricula)
        .options(
            selectinload(Matricula.aluno),
            selectinload(Matricula.disciplina)
        )
        .where(
            Matricula.aluno_id == aluno_id,
            Matricula.disciplina_id == disciplina_id
        )
    )

    result = await db.execute(statement)
    matricula = result.scalar_one_or_none()

    if not matricula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula não encontrada!"
        )

    return matricula


# 4. DELETAR MATRÍCULA (DELETE /matriculas/{aluno_id}/{disciplina_id})
# Apenas coordenadores podem remover
@router.delete("/{aluno_id}/{disciplina_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_matricula(
    aluno_id: int,
    disciplina_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_coordenador)
):
    statement = select(Matricula).where(
        Matricula.aluno_id == aluno_id,
        Matricula.disciplina_id == disciplina_id
    )

    result = await db.execute(statement)
    matricula = result.scalar_one_or_none()

    if not matricula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula não encontrada"
        )

    await db.delete(matricula)
    await db.commit()
    return None