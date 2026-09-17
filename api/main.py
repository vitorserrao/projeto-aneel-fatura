"""Aplicação FastAPI principal.

Exposição: endpoint de saúde, camada de CONSULTA (leitura) e camada de
CÁLCULO de fatura (estimativa linear). Os routers de otimização/EPI/projeção
serão montados nas próximas sprints.
"""

from __future__ import annotations

from fastapi import FastAPI

from api.routers.calculo import router as calculo_router
from api.routers.tarifas import router as consulta_router

app = FastAPI(
    title="Projeto ACR × ACL",
    description="Análise e otimização ACR × ACL (IFSC).",
    version="0.3.0",
)

# Rota de saúde
@app.get("/health", tags=["saude"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# Camada de leitura (consulta tarifária)
app.include_router(consulta_router, prefix="/api", tags=["consulta"])

# Camada de cálculo (fatura ACR) — orquestração repo → adapter → core
app.include_router(calculo_router, prefix="/api", tags=["calculo"])
