/**
 * Histórico de consumo: três entradas (texto colado, tabela editável e CSV)
 * convergem para o MESMO texto de `historico12`, lido por `lerHistorico`.
 * Valor vazio continua vazio (a linha vira erro na validação, nunca zero).
 */
import { MesHistorico } from './api';

/** Linha da tabela editável; strings para preservar o que foi digitado. */
export interface LinhaTabela {
  mes: string; // MM/AAAA
  dPonta: string; // vazio = fatura Verde (demanda única na coluna fora ponta)
  dFora: string;
  ePonta: string;
  eFora: string;
}

const fmt = (v: number | undefined) => (v === undefined ? '' : String(v).replace('.', ','));

export function linhasDeMeses(meses: MesHistorico[]): LinhaTabela[] {
  return meses.map((m) => ({
    mes: `${m.data_referencia.slice(5, 7)}/${m.data_referencia.slice(0, 4)}`,
    dPonta: m.d_med_unica !== undefined ? '' : fmt(m.d_med_ponta),
    dFora: m.d_med_unica !== undefined ? fmt(m.d_med_unica) : fmt(m.d_med_fora_ponta),
    ePonta: fmt(m.e_ponta_kwh),
    eFora: fmt(m.e_fora_ponta_kwh),
  }));
}

/** Tabela → texto: 4 valores (por posto) ou 3 (demanda única) por linha. */
export function textoDeLinhas(linhas: LinhaTabela[]): string {
  return linhas
    .map((l) =>
      l.dPonta.trim() === ''
        ? [l.mes, l.dFora, l.ePonta, l.eFora].join('; ')
        : [l.mes, l.dPonta, l.dFora, l.ePonta, l.eFora].join('; '),
    )
    .join('\n');
}

export const CABECALHO_CSV = 'mes;demanda_ponta_kw;demanda_fora_ponta_kw;consumo_ponta_kwh;consumo_fora_ponta_kwh';

/**
 * CSV → texto do histórico. Aceita ';' ou ',' como separador de colunas
 * (com ',' as casas decimais têm de usar ponto). Linhas de cabeçalho ou de
 * comentário viram comentário ('#'), não erro.
 */
export function textoDeCsv(csv: string): string {
  const linhas = csv.replace(/^﻿/, '').split(/\r?\n/).filter((l) => l.trim() !== '');
  return linhas
    .map((l) => {
      const sep = l.includes(';') ? ';' : ',';
      const cols = l.split(sep).map((c) => c.trim().replace(/^"|"$/g, ''));
      if (!/^\d{1,2}\/\d{4}$/.test(cols[0] ?? '')) return `# ${l}`;
      // Coluna de demanda ponta vazia = fatura Verde (3 valores).
      const valores = cols.slice(1);
      if (valores.length === 4 && valores[0] === '') return [cols[0], ...valores.slice(1)].join('; ');
      return [cols[0], ...valores].join('; ');
    })
    .join('\n');
}

/** Planilha modelo: cabeçalho + os 12 meses anteriores à data de referência, valores em branco. */
export function modeloCsv(dataReferenciaIso: string): string {
  const ok = /^\d{4}-\d{2}/.test(dataReferenciaIso);
  const ano = ok ? Number(dataReferenciaIso.slice(0, 4)) : new Date().getFullYear();
  const mes = ok ? Number(dataReferenciaIso.slice(5, 7)) : new Date().getMonth() + 1;
  const linhas = [CABECALHO_CSV];
  for (let k = 11; k >= 0; k -= 1) {
    const d = new Date(ano, mes - 1 - k, 1);
    linhas.push(`${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()};;;;`);
  }
  return linhas.join('\n') + '\n';
}

/**
 * Meses com consumo muito longe da média do período (indicador para o
 * usuário conferir a digitação; não altera o cálculo).
 */
export function mesesForaDoPadrao(meses: MesHistorico[], limite = 0.25): { mes: string; desvio: number }[] {
  if (meses.length < 3) return [];
  const totais = meses.map((m) => m.e_ponta_kwh + m.e_fora_ponta_kwh);
  const media = totais.reduce((a, x) => a + x, 0) / totais.length;
  if (media <= 0) return [];
  return meses
    .map((m, i) => ({ mes: m.data_referencia, desvio: totais[i] / media - 1 }))
    .filter((x) => Math.abs(x.desvio) > limite);
}
