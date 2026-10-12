from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.matricula import Matricula
from app.schemas import AlunoCreate, AlunoResponse
from app.core import requer_professor, requer_professor_ou_coordenador

router = APIRouter(
    prefix="/alunos",
    tags=["Alunos"]
)


# 1. CRIAR ALUNO (POST /alunos)
# Apenas professores podem criar alunos
@router.post("", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
async def criar_aluno(
    dados: AlunoCreate,
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
            detail=f"Não é possível cadastrar o aluno. O curso com ID {dados.curso_id} não existe."
        )

    novo_aluno = Aluno(
        nome=dados.nome,
        turma=dados.turma,
        curso_id=dados.curso_id
    )

    db.add(novo_aluno)
    await db.commit()


    statement = (
        select(Aluno)
        .options(
            selectinload(Aluno.curso),
            selectinload(Aluno.matricula).selectinload(Matricula.disciplina)
        )
        .where(Aluno.id == novo_aluno.id)
    )

    result = await db.execute(statement)
    return result.scalar_one()



# 2. LISTAR TODOS OS ALUNOS (GET /alunos)
# Professores e coordenadores podem listar
@router.get("", response_model=List[AlunoResponse])
async def listar_alunos(
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor_ou_coordenador)
):
    statement = select(Aluno).options(
        selectinload(Aluno.curso),
        selectinload(Aluno.matricula).selectinload(Matricula.disciplina)
    )

    result = await db.execute(statement)
    return result.scalars().all()


# 3. BUSCAR ALUNO POR ID (GET /alunos/{aluno_id})
# Professores e coordenadores podem buscar
@router.get("/{aluno_id}", response_model=AlunoResponse)
async def buscar_aluno(
    aluno_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor_ou_coordenador)
):
    statement = (
        select(Aluno)
        .options(
            selectinload(Aluno.curso),
            selectinload(Aluno.matricula).selectinload(Matricula.disciplina)
        )
        .where(Aluno.id == aluno_id)
    )

    result = await db.execute(statement)
    aluno = result.scalar_one_or_none()

    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado"
        )

    return aluno


# 4. ATUALIZAR ALUNO (PUT /alunos/{aluno_id})
# Apenas professores podem alterar
@router.put("/{aluno_id}", response_model=AlunoResponse)
async def atualizar_aluno(
    aluno_id: int,
    dados: AlunoCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor)
):
    result_aluno = await db.execute(
        select(Aluno).where(Aluno.id == aluno_id)
    )
    aluno = result_aluno.scalar_one_or_none()

    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado"
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

    aluno.nome = dados.nome
    aluno.turma = dados.turma
    aluno.curso_id = dados.curso_id

    await db.commit()

    statement = (
        select(Aluno)
        .options(
            selectinload(Aluno.curso),
            selectinload(Aluno.matricula).selectinload(Matricula.disciplina)
        )
        .where(Aluno.id == aluno_id)
    )

    result = await db.execute(statement)
    return result.scalar_one()


# 5. DELETAR ALUNO (DELETE /alunos/{aluno_id})
# Apenas professores podem remover
@router.delete("/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_aluno(
    aluno_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(requer_professor)
):
    result = await db.execute(
        select(Aluno).where(Aluno.id == aluno_id)
    )
    aluno = result.scalar_one_or_none()

    if not aluno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluno não encontrado"
        )

    await db.delete(aluno)
    await db.commit()
    return None