"""API SOMENTE-LEITURA do laboratório.

Expõe apenas as consultas ao banco de tarifas ANEEL para os alunos:
- GET /health
- GET /api/distribuidoras
- GET /api/tarifas
- GET /api/tarifas/te-tusd
- GET /api/subgrupos
- GET /api/bandeira
- GET /api/bandeiras

Não monta cálculo/EPI/projeção. CORS aberto para acesso na rede do laboratório.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.tarifas import router as consulta_router

app = FastAPI(
    title="API de Consulta Tarifária ANEEL — Laboratório",
    description="Somente leitura do banco de tarifas (projeto ACR × ACL — IFSC).",
    version="0.3.0-lab",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", tags=["saude"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(consulta_router, prefix="/api", tags=["consulta"])
