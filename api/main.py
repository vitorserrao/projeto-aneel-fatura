"""Aplicação FastAPI principal.

Exposição: endpoint de saúde, camada de CONSULTA (leitura) e camada de
CÁLCULO de fatura (estimativa linear). Os routers de otimização/EPI/projeção
serão montados nas próximas sprints.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.calculo import router as calculo_router
from api.routers.epi import router as epi_router
from api.routers.planejamento import router as planejamento_router
from api.routers.tarifas import router as consulta_router

app = FastAPI(
    title="Projeto ACR × ACL",
    description="Análise e otimização ACR × ACL (IFSC).",
    version="0.3.0",
)

# CORS: frontend (Vite em dev + Vercel em prod). Configure FRONTEND_ORIGINS
# com a lista separada por vírgulas dos domínios permitidos.
_cors_origins = [
    origem.strip()
    for origem in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://localhost:3000,"
        "http://127.0.0.1:5173,http://127.0.0.1:3000",
    ).split(",")
    if origem.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota de saúde
@app.get("/health", tags=["saude"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# Camada de leitura (consulta tarifária)
app.include_router(consulta_router, prefix="/api", tags=["consulta"])

# Camada de cálculo (fatura ACR) — orquestração repo → adapter → core
app.include_router(calculo_router, prefix="/api", tags=["calculo"])

# Camada de PI (Preço de Indiferença) — decisão ACR × ACL
app.include_router(epi_router, prefix="/api", tags=["epi"])

# Camada de planejamento anual (contrato atual × demanda otimizada)
app.include_router(planejamento_router, prefix="/api", tags=["planejamento"])
