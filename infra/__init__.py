"""Camada de infraestrutura.

Responsável por PostgreSQL/SQLAlchemy (conexão, ORM, repositórios) e ingestão
do dataset ANEEL (loader, cleaner, validator). NÃO contém regras de negócio
tarifárias.
"""
