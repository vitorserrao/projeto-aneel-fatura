"""Configuração de conexão com o PostgreSQL via SQLAlchemy.

A conexão é inicializada a partir da variável de ambiente ``DATABASE_URL``
(ver .env.example). Os modelos são SQLModel (``infra/models.py``) e o metadata
de criação de schema é ``SQLModel.metadata``. A engine/sessão continuam sendo
SQLAlchemy (infraestrutura subjacente). O DDL declarativo equivalente está em
``scripts/ddl.sql`` (fonte documental).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Carrega .env se existir (não sobrescreve variáveis já definidas).
load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/projeto_aneel",
)


def create_db_engine(url: str | None = None) -> Engine:
    """Cria a engine de banco. Sem conectividade obrigatória na criação."""
    return create_engine(url or DATABASE_URL, future=True)


def create_session_factory(engine: Engine | None = None):
    """Cria uma sessionmaker associada à engine (ou criada por padrão)."""
    return sessionmaker(bind=engine or create_db_engine(), future=True)


def init_db(engine: Engine | None = None) -> None:
    """Cria as tabelas definidas em ``infra.models`` se ainda não existirem.

    Idempotente: usa ``SQLModel.metadata.create_all``. Não insere dados.
    Equivalente documental: ``scripts/ddl.sql``.
    """
    from . import models as _models  # noqa: F401  garante registro no metadata

    SQLModel.metadata.create_all(bind=engine or create_db_engine())


def ping_db(engine: Engine | None = None) -> bool:
    """Verifica conectividade com o banco (SELECT 1)."""
    eng = engine or create_db_engine()
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
