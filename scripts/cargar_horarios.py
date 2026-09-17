"""Carrega a aba "Horários P, INT e FP" do Simulador de Fatura no banco.

Fonte: Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm
       (C:\\Users\\vitor\\Downloads\\OneDrive_2026-09-10\\Kevin Wu\\Simulador de Fatura)

A aba traz, por distribuidora: Intermediário 1, Horário Ponta, Intermediário 2
e a REH que definiu os horários. A carga casa planilha -> sig_agente do banco
via normalização + tabela de equivalência (confirmada com o usuário).

Uso:
    .venv\\Scripts\\python.exe scripts\\cargar_horarios.py
"""

from __future__ import annotations

import sys
import unicodedata
from datetime import time as time_of_day
from pathlib import Path

# Garante importação de `infra` quando executado de scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import openpyxl
from sqlalchemy import select, text

from infra.database import create_session_factory
from infra.models import Distribuidora

CAMINHO_PLANILHA = (
    r"C:\Users\vitor\Downloads\OneDrive_2026-09-10\Kevin Wu\Simulador de Fatura"
    r"\Ferramenta de Recriar Faturas - Grupo A - sem SCEE.xlsm"
)

ABA = "Horários P, INT e FP"

# Equivalência nome-legível (planilha) -> sig_agente do banco. Usada apenas
# quando a normalização básica não casa. Confirmada com o usuário.
EQUIVALENCIA = {
    "CEA Equatorial": "CEA",
    "Enel GO": "EQUATORIAL GO",
    "Enel SP": "ELETROPAULO",
    "CPFL Piratininga": "CPFL-PIRATININGA",
    "Energisa TO": "ETO",
    "Energisa RO": "ERO",
    "Energisa AC": "EAC",
    "Energisa Borborema": "EBO",
    "Energisa MG": "EMR",
    "Energisa Sul Sudeste": "ESS",
    "Energisa PB": "EPB",
    "Energisa MS": "EMS",
    "Energisa MT": "EMT",
    "Energisa SE": "ESE",
    "Neoenergia Pernambuco": "Neoenergia PE",
    "Neoenergia Coelba": "COELBA",
    "Neoenergia Cosern": "COSERN",
    "Neoenergia Elektro": "ELEKTRO",
    "Celesc-DIS": "CELESC",
    "CEEE Equatorial": "CEEE-D",
    "Light": "LIGHT SESA",
    "Roraima Energia": "ÂMBAR ENERGIA RR",
    "Amazonas Energia": "Âmbar Amazonas",
    "CPFL Santa Cruz (agrupada)": "CPFL SANTA CRUZ",
    "Certel": "CERTEL ENERGIA",
    "Cersad": "CERSAD DISTRIBUI",
    "Creral": "Creral",
    "Nova Palma": "Nova Palma",
    "Forcel": "Forcel",
}

# Distribuidoras "agrupadas": a mesma linha da planilha vale para MAIS DE UMA
# sig_agente do banco.
AGRUPADAS = {
    "RGE (agrupada)": ["RGE", "RGE SUL"],
}


def _norm(s: str) -> str:
    s = "".join(
        c for c in unicodedata.normalize("NFKD", s.upper())
        if not unicodedata.combining(c)
    )
    return s.replace("-", " ").replace("_", " ").replace("  ", " ").strip()


def _hora(texto: str | None, posicao: int) -> time_of_day | None:
    """Extrai a hora (inicio=0, fim=1) de um texto 'HH:MM - HH:MM'."""
    if not texto or "-" not in texto:
        return None
    partes = [p.strip() for p in texto.split("-")]
    if len(partes) < 2:
        return None
    alvo = partes[posicao]
    try:
        h, m = alvo.split(":")
        return time_of_day(int(h), int(m))
    except (ValueError, TypeError):
        return None


def _hora_posicao(texto: str | None, posicao: int) -> float | None:
    """Hora decimal (17.5) por posição: útil só se houver colunas numéricas."""
    return None  # a aba de horários não traz decimais confiáveis; texto basta


def _ler_linhas_planilha() -> list[dict]:
    wb = openpyxl.load_workbook(CAMINHO_PLANILHA, read_only=True, data_only=True)
    ws = wb[ABA]
    linhas = []
    for row in ws.iter_rows(min_row=4, max_row=106, values_only=True):
        # A=vazio; B=número; C=INT1; D=Ponta; E=INT2; F=REH
        nome = row[2]
        if nome is None:
            continue
        nome = str(nome).strip()
        linhas.append({
            "nome": nome,
            "intermedio_1": _texto(row[3]),
            "hora_ponta": _texto(row[4]),
            "intermedio_2": _texto(row[5]),
            "reh": _texto(row[6]),
        })
    return linhas


def _texto(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _buscar_distribuidoras() -> dict[str, Distribuidora]:
    with create_session_factory()() as sess:
        rows = sess.execute(select(Distribuidora)).scalars().all()
        return {d.sig_agente: d for d in rows}


def _inserir(sess, dist_id: int, ln: dict) -> None:
    sess.execute(text("""
        INSERT INTO horario_posto_distribuidora (
            distribuidora_id, intermedio_1, hora_ponta, intermedio_2, reh,
            hora_inicio_int1, hora_fim_int1,
            hora_inicio_ponta, hora_fim_ponta,
            hora_inicio_int2, hora_fim_int2
        ) VALUES (
            :did, :i1, :p, :i2, :reh,
            :hi1, :hf1,
            :hp, :hpf,
            :hi2, :hf2
        )
        ON CONFLICT (distribuidora_id) DO UPDATE SET
            intermedio_1 = EXCLUDED.intermedio_1,
            hora_ponta = EXCLUDED.hora_ponta,
            intermedio_2 = EXCLUDED.intermedio_2,
            reh = EXCLUDED.reh,
            hora_inicio_int1 = EXCLUDED.hora_inicio_int1,
            hora_fim_int1 = EXCLUDED.hora_fim_int1,
            hora_inicio_ponta = EXCLUDED.hora_inicio_ponta,
            hora_fim_ponta = EXCLUDED.hora_fim_ponta,
            hora_inicio_int2 = EXCLUDED.hora_inicio_int2,
            hora_fim_int2 = EXCLUDED.hora_fim_int2
    """), {
        "did": dist_id,
        "i1": ln["intermedio_1"],
        "p": ln["hora_ponta"],
        "i2": ln["intermedio_2"],
        "reh": ln["reh"],
        "hi1": _hora(ln["intermedio_1"], 0),
        "hf1": _hora(ln["intermedio_1"], 1),
        "hp": _hora(ln["hora_ponta"], 0),
        "hpf": _hora(ln["hora_ponta"], 1),
        "hi2": _hora(ln["intermedio_2"], 0),
        "hf2": _hora(ln["intermedio_2"], 1),
    })


def _carregar() -> dict:
    distribuidoras = _buscar_distribuidoras()
    norm_map = {_norm(k): k for k in distribuidoras}

    linhas_planilha = _ler_linhas_planilha()
    carregadas = 0
    nao_casadas: list[str] = []

    with create_session_factory()() as sess:
        for ln in linhas_planilha:
            nome = ln["nome"]

            alvos: list[str] = []
            if nome in EQUIVALENCIA:
                alvos = [EQUIVALENCIA[nome]]
            elif nome in AGRUPADAS:
                alvos = AGRUPADAS[nome]
            else:
                alvo = norm_map.get(_norm(nome))
                if alvo:
                    alvos = [alvo]

            if not alvos:
                nao_casadas.append(nome)
                continue

            for alvo in alvos:
                dist = distribuidoras.get(alvo)
                if dist is None:
                    nao_casadas.append(f"{nome} -> {alvo} (sig ausente no banco)")
                    continue
                _inserir(sess, dist.id, ln)
                carregadas += 1

        sess.commit()

    return {
        "linhas_planilha": len(linhas_planilha),
        "carregadas": carregadas,
        "nao_casadas": nao_casadas,
    }


if __name__ == "__main__":
    resultado = _carregar()
    print("=== Resultado da carga ===")
    print(f"Linhas na planilha: {resultado['linhas_planilha']}")
    print(f"Registros no banco: {resultado['carregadas']}")
    if resultado["nao_casadas"]:
        print("NAO CASADAS (ficaram fora):")
        for n in resultado["nao_casadas"]:
            print(f"  - {n}")
    else:
        print("Todas casaram com sucesso.")
