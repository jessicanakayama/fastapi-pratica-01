from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.curso import Curso
from app.models.disciplina import Disciplina
from app.models.matricula import Matricula
from app.schemas import DisciplinaCreate, DisciplinaResponse
from app.core import requer_professor, requer_professor_ou_coordenador

router = APIRouter(
    prefix="/disciplinas",
    tags=["Disciplinas"]
)


# 1. CRIAR DISCIPLINA (POST /disciplinas)
# Apenas professores podem criar disciplinas
@router.post("", response_model=DisciplinaResponse, status_code=status.HTTP_201_CREATED)
async def criar_disciplina(
    dados: DisciplinaCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor)
):
    result_curso = await db.execute(
        select(Curso).where(Curso.id == dados.curso_id)
    )
    curso_existe = result_curso.scalar_one_or_none()

    if not curso_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível criar a disciplina. O curso com ID {dados.curso_id} não existe."
        )

    nova_disciplina = Disciplina(
        nome=dados.nome,
        carga_horaria=dados.carga_horaria,
        curso_id=dados.curso_id
    )

    db.add(nova_disciplina)
    await db.commit()

    statement = (
        select(Disciplina)
        .options(
            selectinload(Disciplina.curso),
            selectinload(Disciplina.matricula).selectinload(Matricula.aluno)
        )
        .where(Disciplina.id == nova_disciplina.id)
    )

    result = await db.execute(statement)
    return result.scalar_one()


# 2. LISTAR TODAS AS DISCIPLINAS (GET /disciplinas)
# Professores e coordenadores podem listar
@router.get("", response_model=List[DisciplinaResponse])
async def listar_disciplinas(
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor_ou_coordenador)
):
    statement = select(Disciplina).options(
        selectinload(Disciplina.curso),
        selectinload(Disciplina.matricula).selectinload(Matricula.aluno)
    )

    result = await db.execute(statement)
    return result.scalars().all()


# 3. BUSCAR UMA DISCIPLINA POR ID
@router.get("/{disciplina_id}", response_model=DisciplinaResponse)
async def buscar_disciplina(
    disciplina_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor_ou_coordenador)
):
    statement = (
        select(Disciplina)
        .options(
            selectinload(Disciplina.curso),
            selectinload(Disciplina.matricula).selectinload(Matricula.aluno)
        )
        .where(Disciplina.id == disciplina_id)
    )

    result = await db.execute(statement)
    disciplina = result.scalar_one_or_none()

    if not disciplina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada"
        )

    return disciplina


# 4. ATUALIZAR UMA DISCIPLINA
# Apenas professores podem alterar
@router.put("/{disciplina_id}", response_model=DisciplinaResponse)
async def atualizar_disciplina(
    disciplina_id: int,
    dados: DisciplinaCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor)
):
    result_disc = await db.execute(
        select(Disciplina).where(Disciplina.id == disciplina_id)
    )
    disciplina = result_disc.scalar_one_or_none()

    if not disciplina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada"
        )

    result_curso = await db.execute(
        select(Curso).where(Curso.id == dados.curso_id)
    )
    curso_existe = result_curso.scalar_one_or_none()

    if not curso_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Curso com ID {dados.curso_id} não existe."
        )

    disciplina.nome = dados.nome
    disciplina.carga_horaria = dados.carga_horaria
    disciplina.curso_id = dados.curso_id

    await db.commit()

    statement = (
        select(Disciplina)
        .options(
            selectinload(Disciplina.curso),
            selectinload(Disciplina.matricula).selectinload(Matricula.aluno)
        )
        .where(Disciplina.id == disciplina_id)
    )

    result = await db.execute(statement)
    return result.scalar_one()


# 5. DELETAR UMA DISCIPLINA
# Apenas professores podem deletar
@router.delete("/{disciplina_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_disciplina(
    disciplina_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor)
):
    result = await db.execute(
        select(Disciplina).where(Disciplina.id == disciplina_id)
    )
    disciplina = result.scalar_one_or_none()

    if not disciplina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina não encontrada"
        )

    await db.delete(disciplina)
    await db.commit()
    return None