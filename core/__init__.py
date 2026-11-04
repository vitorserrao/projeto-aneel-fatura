"""
Núcleo de regras de negócio tarifário.

Regras rigorosas desta camada:
- É determinística (mesmas entradas + mesmas tarifas = mesmo resultado).
- NÃO depende de infraestrutura (PostgreSQL, FastAPI, Streamlit, Docker,
  APIs externas, arquivos).
- Não consulta banco de dados.
- Não contém valores/fórmulas tarifárias inventados: apenas contratos de
  domínio, aplicação linear de parcelas normalizadas e a fórmula do PI
  (docs/epi.md). Toda regra regulatória pendente falha explicitamente e está
  documentada em docs/premissas.md.
"""

from .models import (
    COMPONENTE_TE,
    COMPONENTE_TUSD,
    GRANDEZA_DEMANDA,
    GRANDEZA_ENERGIA,
    POSTO_FORA_PONTA,
    POSTO_PONTA,
    Consumidor,
    ParcelaCusto,
    ResultadoCalculo,
    ResultadoEPI,
    ResultadoOtimizacao,
    ResultadoPI,
)
from .tarifas import (
    AmbiguidadeTarifaria,
    ParcelaTarifaria,
    TarifaAcr,
    TarifaNaoEncontrada,
    buscar_tarifa,
    filtrar_tarifas,
    selecionar_unica,
    tarifas_vigentes,
)

__all__ = [
    "COMPONENTE_TE",
    "COMPONENTE_TUSD",
    "GRANDEZA_DEMANDA",
    "GRANDEZA_ENERGIA",
    "POSTO_FORA_PONTA",
    "POSTO_PONTA",
    "AmbiguidadeTarifaria",
    "Consumidor",
    "ParcelaCusto",
    "ParcelaTarifaria",
    "ResultadoCalculo",
    "ResultadoEPI",
    "ResultadoOtimizacao",
    "ResultadoPI",
    "TarifaAcr",
    "TarifaNaoEncontrada",
    "buscar_tarifa",
    "filtrar_tarifas",
    "selecionar_unica",
    "tarifas_vigentes",
]
