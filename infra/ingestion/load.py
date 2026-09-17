"""Carga transacional do dataset ANEEL no PostgreSQL.

Pipeline: ler CSV (loader) → normalizar (cleaner) → validar/gerar componentes
(validator) → persistir em transação única. Em qualquer erro, rollback — nunca
deixa carga parcialmente inserida (Sprint 3).
"""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

from sqlalchemy.future import select

from ..database import create_session_factory
from ..models import Acessante, CargaAneel, Distribuidora, TarifaAplicacaoComponente
from . import cleaner
from .loader import carregar_dataset
from .validator import componentes_do_registro, validar_registro


class CargaAneelError(RuntimeError):
    """Falha na carga do dataset (rollback aplicado)."""


def _sha256(caminho: str) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()


class PipelineIngestao:
    """Orquestra a ingestão de um CSV da ANEEL em uma transação."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or create_session_factory()

    def executar(self, caminho_csv: str, *, observacoes: str | None = None) -> dict[str, object]:
        path = Path(caminho_csv)
        sha = _sha256(str(path))

        # --- 1. Se já existe carga com este SHA, não reingere (idempotência).
        with self._session_factory() as sess:
            existe = sess.execute(
                select(CargaAneel).where(CargaAneel.sha256_arquivo == sha)
            ).scalar_one_or_none()
            if existe is not None:
                raise CargaAneelError(
                    f"carga já registrada para este SHA-256 ({sha}); "
                    "segunda execução detectada — não reingere."
                )

        # --- 2. Primeira passada: ler cópia limpa em memória + contagens.
        distribuicoes: dict[str, str] = {}  # cnpj -> sig
        acessantes: set[str] = set()
        dat_geracao: date | None = None
        componentes: list[dict[str, object]] = []

        n = 0
        for raw in carregar_dataset(str(path)):
            n += 1
            norm = cleaner.normalizar_registro(raw)
            reg = validar_registro(norm)
            distribuicoes.setdefault(reg.num_cnpj, reg.sig_agente)
            if reg.sig_acessante:
                acessantes.add(reg.sig_acessante)
            dat_geracao = reg.dat_geracao
            for comp in componentes_do_registro(reg):
                componentes.append(
                    {
                        **comp,
                        "cnpj": reg.num_cnpj,
                        "dat_inicio": reg.dat_inicio,
                        "dat_fim": reg.dat_fim,
                        "dsc_reh": reg.dsc_reh,
                        "dsc_base": reg.dsc_base_tarifaria,
                        "dsc_sub": reg.dsc_sub_grupo,
                        "dsc_mod": reg.dsc_modalidade,
                        "dsc_cla": reg.dsc_classe,
                        "dsc_sub_cla": reg.dsc_sub_classe,
                        "dsc_det": reg.dsc_detalhe,
                        "nom_posto": reg.nom_posto,
                        "dsc_uni": reg.dsc_unidade,
                        "sig_acess": reg.sig_acessante,
                    }
                )

        # --- 3. Persistência transacional.
        try:
            with self._session_factory() as sess:
                dist_ids: dict[str, int] = {}
                for cnpj, sig in distribuicoes.items():
                    d = Distribuidora(num_cnpj=cnpj, sig_agente=sig)
                    sess.add(d)
                    sess.flush()
                    dist_ids[cnpj] = d.id

                acess_ids: dict[str, int] = {}
                for sig in sorted(acessantes):
                    a = Acessante(sig_acessante=sig)
                    sess.add(a)
                    sess.flush()
                    acess_ids[sig] = a.id

                carga = CargaAneel(
                    arquivo_origem=str(path),
                    sha256_arquivo=sha,
                    dat_geracao_conjunto=dat_geracao,
                    num_registros=n,
                    observacoes=observacoes,
                )
                sess.add(carga)
                sess.flush()

                for c in componentes:
                    conteudo_hash = f"{sha}|{c['linha_origem']}|{c['componente']}".encode()
                    sess.add(
                        TarifaAplicacaoComponente(
                            carga_id=carga.id,
                            distribuidora_id=dist_ids[c["cnpj"]],
                            acessante_id=acess_ids.get(c["sig_acess"]),
                            dsc_reh=c["dsc_reh"],
                            dat_inicio_vigencia=c["dat_inicio"],
                            dat_fim_vigencia=c["dat_fim"],
                            dsc_base_tarifaria=c["dsc_base"],
                            dsc_sub_grupo=c["dsc_sub"],
                            dsc_modalidade_tarifaria=c["dsc_mod"],
                            dsc_classe=c["dsc_cla"],
                            dsc_sub_classe=c["dsc_sub_cla"],
                            dsc_detalhe=c["dsc_det"],
                            nom_posto_tarifario=c["nom_posto"],
                            dsc_unidade_terciaria=c["dsc_uni"],
                            componente=c["componente"],
                            valor=c["valor"],
                            linha_origem=c["linha_origem"],
                            hash_linha=hashlib.sha256(conteudo_hash).hexdigest(),
                        )
                    )
                sess.commit()
                carga_id = carga.id
        except Exception as exc:
            raise CargaAneelError(f"falha na carga (rollback): {exc}") from exc

        return {
            "carga_id": carga_id,
            "sha256": sha,
            "linhas_csv": n,
            "distribuidoras": len(distribuicoes),
            "acessantes": len(acessantes),
            "componentes": len(componentes),
        }
