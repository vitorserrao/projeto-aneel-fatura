"""Validação camada 1 — motor com as tarifas líquidas da própria fatura.

Carrega os casos de ``docs/validacao_faturas_reais/casos/*.json``, monta as
parcelas a partir das tarifas líquidas da fatura e compara linha a linha com os
valores impressos na fatura (``linhas_esperadas``). Não consulta o banco.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.motor_calculo import calcular_fatura
from core.models import Consumidor
from core.tarifas import ParcelaTarifaria

CASOS = Path("docs/validacao_faturas_reais/casos")


def _carregar(nome: str) -> dict:
    return json.loads((CASOS / nome).read_text(encoding="utf-8"))


def _parcelas(caso: dict) -> list[ParcelaTarifaria]:
    parcelas = []
    for t in caso["tarifas_liquidas"]:
        if t["componente"] == "REATIVO":
            continue
        grandeza = t["grandeza"]
        posto = t["posto"]
        unidade = t["unidade"]
        valor = t["valor"]
        if unidade == "R$/kWh":
            unidade = "R$/MWh"
            valor = valor * 1000
        parcelas.append(
            ParcelaTarifaria(t["componente"], grandeza, posto, unidade, valor)
        )
    return parcelas


def _consumidor(caso: dict) -> Consumidor:
    p = caso["perfil"]
    return Consumidor(
        distribuidora=caso["meta"]["distribuidora"],
        subgrupo=caso["meta"]["subgrupo"],
        classe="Não se aplica",
        subclasse="Não se aplica",
        detalhe="Não se aplica",
        data_referencia=date.fromisoformat(p["data_referencia"]),
        consumo_ponta_kwh=p["consumo_ponta_kwh"],
        consumo_fora_ponta_kwh=p["consumo_fora_ponta_kwh"],
        demanda_ponta_kw=p.get("demanda_ponta_kw", 0.0),
        demanda_fora_ponta_kw=p.get("demanda_fora_ponta_kw", 0.0),
        demanda_contratada_ponta_kw=p.get("demanda_contratada_ponta_kw", 0.0),
        demanda_contratada_fora_ponta_kw=p.get("demanda_contratada_fora_ponta_kw", 0.0),
        demanda_medida_unica_kw=p.get("demanda_medida_unica_kw", 0.0),
        demanda_contratada_unica_kw=p.get("demanda_contratada_unica_kw", 0.0),
        reativo_energia_ponta_kvArh=p.get("reativo_energia_ponta_kvArh", 0.0),
        reativo_energia_fora_ponta_kvArh=p.get("reativo_energia_fora_ponta_kvArh", 0.0),
        cip_cosip_rs=p.get("cip_cosip_rs", 0.0),
        outros_rs=p.get("outros_rs", 0.0),
        bandeira_adicional_r_kwh=p.get("bandeira_adicional_r_kwh", 0.0),
    )


def _tarifa_reativo(caso: dict) -> float | None:
    for t in caso["tarifas_liquidas"]:
        if t["componente"] == "REATIVO":
            return float(t["valor"])
    return None


def _linhas_motor(caso: dict) -> dict:
    trib = caso["tributos"]
    parc = _parcelas(caso)
    tarifa_reativo = _tarifa_reativo(caso)
    fatura = calcular_fatura(
        _consumidor(caso),
        caso["meta"]["modalidade"],
        parc,
        demanda_unica=caso["meta"]["modalidade"] == "Verde",
        aplicar_tributos=True,
        pis=trib["pis"],
        cofins=trib["cofins"],
        icms=trib["icms"],
        tipo_icms=trib["tipo_icms"],
        reativos_direto=tarifa_reativo is not None,
        tarifa_reativo_energia_r_kvarh=tarifa_reativo,
        arredondar_centavos=True,
    )
    linhas = {}
    for l in fatura.linhas:
        linhas[l.descricao] = round(l.custo, 2)
    return linhas


def _comparar_por_palavras(linhas_motor: dict, esperadas: list[dict]) -> None:
    for e in esperadas:
        d = e["descricao"].lower()
        valor = e["valor"]
        alvo = None
        # regras de mapeamento por palavras-chave
        if "te ponta" in d or ("te " in d and "ponta" in d and "f ponta" not in d and "f. ponta" not in d):
            alvo = next((v for k, v in linhas_motor.items() if "TE ENERGIA PONTA" in k), None)
        elif "te f ponta" in d or "te f. ponta" in d or ("te " in d and "fora ponta" in d):
            alvo = next((v for k, v in linhas_motor.items() if "TE ENERGIA FORA PONTA" in k), None)
        elif "usd ponta" in d or "tusd" in d and "ponta" in d:
            alvo = next((v for k, v in linhas_motor.items() if "TUSD ENERGIA PONTA" in k), None)
        elif "usd f ponta" in d or ("tusd" in d and "fora ponta" in d):
            alvo = next((v for k, v in linhas_motor.items() if "TUSD ENERGIA FORA PONTA" in k), None)
        elif "demanda" in d and "reativ" not in d:
            alvo = sum(v for k, v in linhas_motor.items() if "TUSD DEMANDA" in k)
        elif "reativ" in d and "demanda" not in d:
            alvo = sum(v for k, v in linhas_motor.items() if "reativa" in k.lower() or "reativo" in k.lower())
        elif "ilum" in d or "cip" in d or "cosip" in d:
            alvo = sum(v for k, v in linhas_motor.items() if "CIP/COSIP" in k or "ENCARGO" in k)
        if alvo is not None:
            diff = round(valor - alvo, 2)
            print(f"  {e['descricao'][:44]:46s} fatura={valor:>12,.2f} motor={alvo:>12,.2f} diff={diff:>+8,.2f}")
        else:
            print(f"  {e['descricao'][:44]:46s} fatura={valor:>12,.2f} motor=<sem mapeamento>")


def main() -> None:
    for nome in sorted(CASOS.glob("*.json")):
        caso = _carregar(nome.name)
        print("=" * 100)
        print(f"{caso['meta']['distribuidora']} | {caso['meta']['modalidade']} | {caso['meta']['competencia']} | total fatura {caso['meta']['total_fatura']:,.2f}")
        linhas = _linhas_motor(caso)
        print(f"  Total motor (camada 1): {sum(linhas.values()):,.2f}")
        _comparar_por_palavras(linhas, caso["linhas_esperadas"])
        for nota in caso.get("notas", []):
            print(f"  NOTA: {nota}")


if __name__ == "__main__":
    main()
