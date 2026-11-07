"""Serviço de PI (Preço de Indiferença) — orquestração repo → core.

Caso de uso: dado um perfil ACR, buscar as TE (sem tributos) da modalidade de
menor custo no ACR e a bandeira vigente, e chamar ``core.epi.calcular_pi``
(fórmula adaptada de Lemos, 2025 — ver docs/epi.md).

Regra de busca de TE (alinhada à Seção 3.2.1 do TCC):
- base ``Tarifa de Aplicação``;
- componente TE, unidade MWh;
- detalhe ``"Não se aplica"`` (exclui linhas como SCEE/APE);
- vigência na data de referência;
- valores distintos do MESMO posto são somados (TE total = soma das linhas
  TE); repetições de valor idêntico são deduplicadas.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from core.epi import calcular_pi
from core.motor_calculo import tarifa_b_do_optante
from core.models import (
    POSTO_FORA_PONTA,
    POSTO_PONTA,
    Consumidor,
    ResultadoPI,
)

from .calculo_service import BASE_PADRAO
from .otimizacao_service import OtimizacaoService


@dataclass(frozen=True)
class ResultadoServicoPI:
    """Resultado do serviço: PI + modalidade ACR usada + bandeira vigente."""

    resultado: ResultadoPI
    modalidade: str
    bandeira_r_mwh: float


class EPIService:
    """Caso de uso: calcular o Preço de Indiferença (PI)."""

    def __init__(self, tarifa_repository, otimizacao_service: OtimizacaoService):
        self._repo = tarifa_repository
        self._otimizacao = otimizacao_service

    def calcular(
        self,
        perfil: Consumidor,
        *,
        pis: float,
        cofins: float,
        icms: float,
        k: float = 0.03,
        encargos: float = 0.0,
        opex_mensal: float = 0.0,
        capex: float = 0.0,
        horizonte_meses: int = 60,
        modalidade: str | None = None,
    ) -> ResultadoServicoPI:
        """Calcula o PI para o ``perfil``.

        Args:
            perfil: perfil ACR (consumo em kWh; data de referência para
                vigência das tarifas e da bandeira).
            pis, cofins, icms: alíquotas de tributos (fração).
            k: perdas na migração ao ACL (fração). Padrão 0,03.
            encargos: encargos do ACL por energia (R$/MWh, ex.: ESS).
            opex_mensal, capex, horizonte_meses: custos do ACL.
            modalidade: modalidade ACR a usar (ex.: "Azul"). ``None`` = a de
                menor custo no ACR (via ``OtimizacaoService``).

        Returns:
            ``ResultadoServicoPI`` com o ``ResultadoPI``, a modalidade usada
            e a bandeira vigente (R$/MWh).

        Raises:
            ValueError: TE indisponível/ambígua, modalidade inválida ou
                parâmetros inválidos (repassados do core).
        """
        data_ref = perfil.data_referencia or date.today()

        if modalidade is None:
            escolhida = self._otimizacao.otimizar(perfil).modalidade_escolhida
        else:
            escolhida = modalidade.strip().upper()
            if escolhida not in ("AZUL", "VERDE", "OPTANTE B"):
                raise ValueError(
                    f"modalidade {modalidade!r} não suportada no PI; use "
                    "Azul, Verde ou Optante B (ou None para menor custo)"
                )
        modalidade_db = escolhida.strip().title()

        te_ponta, te_fora_ponta = self._buscar_te(
            perfil, modalidade_db, data_ref
        )

        bandeira_r_mwh = 0.0
        bandeira = self._repo.buscar_bandeira(data_ref)
        if bandeira is not None:
            bandeira_r_mwh = bandeira[2]  # (bandeira, valor_kwh, valor_mwh)

        e_ponta_mwh = perfil.consumo_ponta_kwh / 1000.0
        e_fora_ponta_mwh = perfil.consumo_fora_ponta_kwh / 1000.0

        resultado = calcular_pi(
            e_ponta=e_ponta_mwh,
            e_fora_ponta=e_fora_ponta_mwh,
            te_ponta=te_ponta,
            te_fora_ponta=te_fora_ponta,
            pis=pis,
            cofins=cofins,
            icms=icms,
            bandeira=bandeira_r_mwh,
            encargos=encargos,
            k=k,
            opex_mensal=opex_mensal,
            capex=capex,
            horizonte_meses=horizonte_meses,
        )
        return ResultadoServicoPI(
            resultado=resultado,
            modalidade=escolhida,
            bandeira_r_mwh=bandeira_r_mwh,
        )

    # ------------------------------------------------------------------ #
    # Busca de TE
    # ------------------------------------------------------------------ #
    def _buscar_te(
        self, perfil: Consumidor, modalidade_db: str, data_ref: date
    ) -> tuple[float, float]:
        # O dataset ANEEL não publica a modalidade "Optante B": a unidade do
        # Grupo A enquadrada no art. 292 é faturada pela Convencional do
        # subgrupo B derivado da atividade (mesma regra da fatura — ver
        # core.motor_calculo.tarifa_b_do_optante).
        subgrupo_busca = perfil.subgrupo
        classe_filtro = None
        subclasse_filtro = None
        caminho_b = modalidade_db.strip().casefold() == "optante b"
        if caminho_b:
            contexto = tarifa_b_do_optante(perfil.atividade)
            subgrupo_busca = contexto.subgrupo
            modalidade_db = contexto.modalidade
            classe_filtro = contexto.classe
            subclasse_filtro = contexto.subclasse

        tarifas = self._repo.buscar_tarifas(
            data=data_ref,
            sig_agente=perfil.distribuidora,
            subgrupo=subgrupo_busca,
            modalidade=modalidade_db,
            componente="TE",
            unidade="MWh",
            detalhe="Não se aplica",
            base_tarifaria=BASE_PADRAO,
            classe=classe_filtro,
            subclasse=subclasse_filtro,
        )

        valores_por_posto: dict[str, set[float]] = {
            POSTO_PONTA: set(),
            POSTO_FORA_PONTA: set(),
        }
        for t in tarifas:
            posto = self._posto_de(t.posto)
            if posto is not None:
                valores_por_posto[posto].add(float(t.valor))
            elif "aplica" in t.posto.casefold():
                # Tarifa única (monômia, ex.: Optante B): o dataset grafa
                # posto "Não se aplica" — vale igual para ponta e fora ponta.
                valores_por_posto[POSTO_PONTA].add(float(t.valor))
                valores_por_posto[POSTO_FORA_PONTA].add(float(t.valor))

        # Só no caminho B: no Grupo A somar TE distintas do mesmo posto é a
        # regra documentada (TE total = soma das linhas). No Optante B a TE é
        # uma tarifa única por chave: mais de um valor distinto no mesmo posto
        # significa classe ambígua (ex.: B1 Residencial × Baixa Renda) e somar
        # inflaria o PI (A5/P6) — recusamos dizendo o que informar.
        if caminho_b and classe_filtro is None:
            for posto, valores in valores_por_posto.items():
                if len(valores) > 1:
                    raise ValueError(
                        "TE ambígua para "
                        f"{perfil.distribuidora} {subgrupo_busca} "
                        f"{modalidade_db} ({posto}) na data "
                        f"{data_ref.isoformat()}: {len(valores)} valores "
                        "vigentes distintos. Informe a atividade econômica "
                        "do optante para desambiguar a classe (art. 292)."
                    )

        te_por_posto = {
            posto: sum(valores) for posto, valores in valores_por_posto.items()
        }
        if te_por_posto[POSTO_PONTA] <= 0 or te_por_posto[POSTO_FORA_PONTA] <= 0:
            raise ValueError(
                "TE indisponível para "
                f"{perfil.distribuidora} {subgrupo_busca} {modalidade_db} "
                f"na data {data_ref.isoformat()} (detalhe 'Não se aplica', "
                "base Tarifa de Aplicação). Verifique distribuidora/subgrupo/"
                "modalidade/data."
            )
        return te_por_posto[POSTO_PONTA], te_por_posto[POSTO_FORA_PONTA]

    @staticmethod
    def _posto_de(posto: str) -> str | None:
        """Normaliza o posto do dataset para PONTA/FORA PONTA."""
        p = posto.strip().casefold()
        if "fora" in p:
            return POSTO_FORA_PONTA
        if "ponta" in p:
            return POSTO_PONTA
        return None
