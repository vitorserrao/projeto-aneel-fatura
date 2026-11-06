/**
 * Regras de entrada do simulador (docs/entradas.md).
 *
 * Princípio: o que o usuário não informou NUNCA vira zero escondido.
 * - Obrigatório vazio → bloqueia o cálculo com mensagem.
 * - Opcional vazio → usa um padrão declarado e listado no relatório.
 * - Histórico: usa só os meses informados (mínimo = o mês da fatura).
 */
import { InvoiceFormData } from '../types/energy';
import { num, vazio } from './numeros';
import { dataReferenciaIso, lerHistorico, MesHistorico } from './api';

export { vazio, num };

export const ehGrupoA = (form: InvoiceFormData): boolean =>
  form.subgrupo.trim().toUpperCase().startsWith('A');

/** O usuário informou algum critério do art. 292 (transformadores, hotelaria ou refletores)? */
export const optanteBInformado = (form: InvoiceFormData): boolean =>
  !vazio(form.potenciaTransformadoresKva) ||
  form.hotelariaTurismo ||
  (form.cargaRefletoresKw > 0 && form.cargaInstaladaTotalKw > 0);

function dataValida(txt: string): boolean {
  const iso = dataReferenciaIso(txt);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return false;
  const d = new Date(`${iso}T12:00:00`);
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === iso;
}

/** Lista do que falta ou está inconsistente. Vazia = pode calcular. */
export function validarFormulario(form: InvoiceFormData): string[] {
  const p: string[] = [];
  const mod = form.modalidadeAtual;
  const grupoA = ehGrupoA(form);

  if (!form.distribuidora.trim()) p.push('Distribuidora');
  if (!form.subgrupo.trim()) p.push('Subgrupo');
  if (!dataValida(form.dataReferencia)) p.push('Data de referência (DD/MM/AAAA)');

  // Modalidade × subgrupo
  if (form.subgrupo.trim() && (mod === 'verde' || mod === 'azul' || mod === 'optante_b') && !grupoA) {
    p.push(`Modalidade ${mod === 'optante_b' ? 'Optante B' : mod} exige subgrupo do Grupo A`);
  }
  if (form.subgrupo.trim() && (mod === 'branca' || mod === 'convencional') && grupoA) {
    p.push('Branca/Convencional exigem subgrupo do Grupo B (B1–B4)');
  }

  // Consumo
  if (grupoA || mod === 'branca' || !form.subgrupo.trim()) {
    if (vazio(form.consumoPonta)) p.push('Consumo ponta (kWh) — digite 0 se não houve consumo na ponta');
    if (vazio(form.consumoForaPonta)) p.push('Consumo fora de ponta (kWh)');
  } else if (vazio(form.consumoForaPonta) && vazio(form.consumoPonta)) {
    p.push('Consumo (kWh)');
  }
  if (mod === 'branca' && vazio(form.consumoIntermediario)) p.push('Consumo intermediário (kWh)');
  const total = num(form.consumoPonta) + num(form.consumoForaPonta) + num(form.consumoIntermediario);
  if (total <= 0 && p.every((x) => !x.startsWith('Consumo'))) p.push('Consumo total maior que zero');

  // Demanda
  if (mod === 'verde') {
    if (vazio(form.demandaMedida)) p.push('Demanda medida única (kW)');
    if (vazio(form.demandaContratada)) p.push('Demanda contratada única (kW)');
    else if (num(form.demandaContratada) < 30) p.push('Demanda contratada ≥ 30 kW (mínimo do Grupo A)');
  }
  if (mod === 'azul') {
    if (vazio(form.demandaPontaKw)) p.push('Demanda medida ponta (kW)');
    if (vazio(form.demandaForaPontaKw)) p.push('Demanda medida fora de ponta (kW)');
    if (vazio(form.demandaContratadaPontaKw)) p.push('Demanda contratada ponta (kW)');
    if (vazio(form.demandaContratadaForaPontaKw)) p.push('Demanda contratada fora de ponta (kW)');
  }

  // Optante B como modalidade atual exige o critério do art. 292
  if (mod === 'optante_b' && !optanteBInformado(form)) {
    p.push('Optante B: informe a potência dos transformadores (kVA) ou o critério de hotelaria/refletores');
  }

  // Tributos
  if (form.aplicarTributos) {
    if (vazio(form.pis)) p.push('PIS (%)');
    if (vazio(form.cofins)) p.push('COFINS (%)');
    if (vazio(form.icms)) p.push('ICMS (%) — digite 0 se a unidade é isenta');
  }

  // Reativo em modo manual: tarifa precisa existir se houver excedente
  const temReativo =
    form.consumoReativoPonta + form.consumoReativoForaPonta + form.reativoEnergiaCapacitiva > 0 ||
    form.demandaReativaPonta + form.demandaReativaForaPonta + form.reativoDemandaCapacitiva > 0;
  if (temReativo && !form.buscarReativoAuto) {
    if (form.tarifaReativoEnergia <= 0 && form.consumoReativoPonta + form.consumoReativoForaPonta + form.reativoEnergiaCapacitiva > 0)
      p.push('Tarifa de energia reativa (R$/kVArh) — ou ative a busca automática');
    if (form.tarifaReativoDemanda <= 0 && form.demandaReativaPonta + form.demandaReativaForaPonta + form.reativoDemandaCapacitiva > 0)
      p.push('Tarifa de demanda reativa (R$/kVAr) — ou ative a busca automática');
  }

  // E-PI com custos: CAPEX exige horizonte
  if (form.capex > 0 && !(form.horizonteMeses > 0)) p.push('Meses de amortização do CAPEX');

  // Histórico: linhas ilegíveis bloqueiam (não são descartadas em silêncio)
  const { erros } = lerHistorico(form.historico12);
  for (const e of erros) p.push(`Histórico — ${e}`);

  return p;
}

/** Mês da fatura (formulário) no formato do planejamento; null fora de Verde/Azul. */
export function mesDoFormulario(form: InvoiceFormData): MesHistorico | null {
  const iso = dataReferenciaIso(form.dataReferencia);
  const base = {
    data_referencia: `${iso.slice(0, 7)}-15`,
    e_ponta_kwh: num(form.consumoPonta),
    e_fora_ponta_kwh: num(form.consumoForaPonta),
  };
  if (form.modalidadeAtual === 'verde') return { ...base, d_med_unica: num(form.demandaMedida) };
  if (form.modalidadeAtual === 'azul')
    return { ...base, d_med_ponta: num(form.demandaPontaKw), d_med_fora_ponta: num(form.demandaForaPontaKw) };
  return null;
}

const quase = (a: number, b: number) => Math.abs(a - b) < 0.01;

/** Linha do histórico e mês do formulário descrevem a mesma fatura? */
function mesmoMes(h: MesHistorico, f: MesHistorico): boolean {
  if (!quase(h.e_ponta_kwh, f.e_ponta_kwh) || !quase(h.e_fora_ponta_kwh, f.e_fora_ponta_kwh)) return false;
  const maxH = h.d_med_unica ?? Math.max(h.d_med_ponta ?? 0, h.d_med_fora_ponta ?? 0);
  const maxF = f.d_med_unica ?? Math.max(f.d_med_ponta ?? 0, f.d_med_fora_ponta ?? 0);
  return quase(maxH, maxF);
}

const mmaaaa = (iso: string) => `${iso.slice(5, 7)}/${iso.slice(0, 4)}`;

/**
 * Meses do planejamento: histórico informado + mês da fatura.
 * - sem histórico → só o mês da fatura (resultado parcial/indicativo);
 * - mês da fatura já no histórico → valem os valores do formulário;
 * - mais de 12 → os 12 mais recentes;
 * - nenhum mês é inventado ou completado com zero.
 */
export function montarMesesPlanejamento(form: InvoiceFormData): {
  meses: MesHistorico[];
  avisos: string[];
  periodo: string;
} {
  const avisos: string[] = [];
  const { meses: hist } = lerHistorico(form.historico12);
  const doForm = mesDoFormulario(form);
  const porMes = new Map<string, MesHistorico>();
  for (const m of hist) porMes.set(m.data_referencia.slice(0, 7), m);
  if (doForm) {
    const chave = doForm.data_referencia.slice(0, 7);
    const h = porMes.get(chave);
    if (!h) {
      porMes.set(chave, doForm);
    } else if (!mesmoMes(h, doForm)) {
      avisos.push(`O mês ${mmaaaa(chave)} do histórico difere do formulário; foram usados os valores do formulário.`);
      porMes.set(chave, doForm);
    }
    // iguais: mantém a linha do histórico (pode ter demanda por posto, mais detalhada)
  }
  let meses = [...porMes.values()].sort((a, b) => a.data_referencia.localeCompare(b.data_referencia));
  if (meses.length > 12) {
    avisos.push(`Foram informados ${meses.length} meses; o planejamento usa os 12 mais recentes.`);
    meses = meses.slice(-12);
  }
  // Lacunas entre meses
  for (let i = 1; i < meses.length; i += 1) {
    const a = new Date(`${meses[i - 1].data_referencia}T12:00:00`);
    const b = new Date(`${meses[i].data_referencia}T12:00:00`);
    const dif = (b.getFullYear() - a.getFullYear()) * 12 + (b.getMonth() - a.getMonth());
    if (dif > 1) {
      avisos.push('Há meses faltando no histórico; eles não entram no cálculo (não são tratados como zero).');
      break;
    }
  }
  if (meses.length === 1) {
    avisos.push(
      'Planejamento com 1 mês (sem histórico): a demanda ótima é indicativa e o ganho não é anualizado. ' +
        'Picos de outros meses podem exigir uma demanda contratada maior.',
    );
  } else if (meses.length < 12) {
    avisos.push(
      `Planejamento com ${meses.length} meses: valores somados só nesses meses (sem extrapolar para 12). ` +
        'Picos dos meses ausentes podem exigir uma demanda contratada maior.',
    );
  }
  if (meses.some((m) => m.d_med_unica !== undefined) && meses.some((m) => m.d_med_ponta === undefined)) {
    avisos.push(
      'Histórico com demanda única (fatura Verde): a simulação Azul usa o mesmo valor na ponta e fora de ponta, ' +
        'o que superestima o custo de demanda na ponta da Azul.',
    );
  }
  const periodo =
    meses.length > 0
      ? meses.length === 1
        ? mmaaaa(meses[0].data_referencia)
        : `${mmaaaa(meses[0].data_referencia)}–${mmaaaa(meses[meses.length - 1].data_referencia)}`
      : '';
  return { meses, avisos, periodo };
}

/** Premissas assumidas por falta de dado opcional (aparecem no relatório). */
export function premissasDeEntrada(form: InvoiceFormData): string[] {
  const p: string[] = [];
  if (ehGrupoA(form) && form.modalidadeAtual !== 'optante_b' && !optanteBInformado(form)) {
    p.push('Optante B não avaliado: a potência dos transformadores (kVA) não foi informada.');
  }
  if (vazio(form.encargosAcl)) {
    p.push('E-PI sem encargos do ACL (ESS/EER, CCEE): informe em R$/MWh para um E-PI mais conservador.');
  }
  if (!(form.opexMensal > 0) && !(form.capex > 0)) {
    p.push('E-PI simplificado: sem OPEX/CAPEX de migração.');
  }
  const semReativo =
    form.consumoReativoPonta + form.consumoReativoForaPonta + form.demandaReativaPonta +
      form.demandaReativaForaPonta + form.reativoEnergiaCapacitiva + form.reativoDemandaCapacitiva === 0;
  if (semReativo && ehGrupoA(form)) p.push('Reativo excedente não informado: não foi cobrado.');
  if (!form.aplicarTributos) p.push('Valores sem tributos (PIS/COFINS/ICMS desligados).');
  if (vazio(form.totalFatura)) p.push('Total da fatura não informado: sem conferência com a conta real.');
  return p;
}
