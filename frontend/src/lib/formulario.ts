/**
 * Regras de visibilidade do formulário (B9): o que some da tela deixa de
 * valer. Ao trocar de modalidade, os campos que não se aplicam voltam a
 * vazio (null) ou ao padrão declarado — nunca ficam com o valor de um
 * exemplo anterior escondido no estado.
 */
import type { InvoiceFormData, TariffModalidade } from '../types/energy';

const DEMANDA_UNICA = ['demandaMedida', 'demandaContratada'] as const;
const DEMANDA_POSTOS = ['demandaPontaKw', 'demandaForaPontaKw', 'demandaContratadaPontaKw', 'demandaContratadaForaPontaKw'] as const;

/** Campos de demanda visíveis em cada modalidade. */
export function camposDemandaVisiveis(mod: TariffModalidade): readonly (keyof InvoiceFormData)[] {
  if (mod === 'verde') return DEMANDA_UNICA;
  if (mod === 'azul') return DEMANDA_POSTOS;
  // Optante B: demanda única opcional, só para comparar com o Grupo A (B11).
  if (mod === 'optante_b') return DEMANDA_UNICA;
  return [];
}

export function trocarModalidade(form: InvoiceFormData, nova: TariffModalidade): InvoiceFormData {
  if (form.modalidadeAtual === nova) return form;
  const f: InvoiceFormData = { ...form, modalidadeAtual: nova };
  const visiveis = new Set(camposDemandaVisiveis(nova));
  for (const c of [...DEMANDA_UNICA, ...DEMANDA_POSTOS]) {
    // Ao entrar no Optante B, a demanda do Grupo A não é dado da unidade:
    // começa vazia (o usuário informa se quiser comparar).
    if (!visiveis.has(c) || nova === 'optante_b') (f[c] as number | null) = null;
  }
  if (nova !== 'verde' && nova !== 'azul') {
    f.demandaIsentaIcms = 0;
  }
  if (nova !== 'branca') f.consumoIntermediario = null;
  if (nova !== 'optante_b') {
    // Critérios do art. 292 só aparecem no Optante B.
    f.potenciaTransformadoresKva = null;
    f.hotelariaTurismo = false;
    f.cooperativaEletrificacaoRural = false;
    f.cargaRefletoresKw = 0;
    f.cargaInstaladaTotalKw = 0;
  }
  return f;
}
