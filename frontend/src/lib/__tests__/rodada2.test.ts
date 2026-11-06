/**
 * Rodada 2 do handoff: B7 e B9–B13, com a API simulada (apiFake).
 * Exemplo Optante B no formato da fatura Equatorial Tucuruí 12/2024.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { instalarApiFake } from './apiFake';
import { DEFAULT_FORM, exemploCopel } from '../formPadrao';
import { conferir, executarAnalise, recomendacaoMes } from '../analise';
import { bandeiraParaApi, paraConsumidor } from '../api';
import { trocarModalidade } from '../formulario';
import type { FaturaModalidade } from '../cenarios';
import type { PlanejamentoApi } from '../api';
import type { InvoiceFormData } from '../../types/energy';

afterEach(() => vi.unstubAllGlobals());

/** Optante B no formato da fatura Equatorial Tucuruí 12/2024. */
const tucurui = (): InvoiceFormData => ({
  ...DEFAULT_FORM,
  distribuidora: 'EQUATORIAL PA',
  subgrupo: 'A4',
  dataReferencia: '15/12/2024',
  modalidadeAtual: 'optante_b',
  potenciaTransformadoresKva: 75,
  consumoPonta: 0,
  consumoForaPonta: 2665,
  consumoReativoForaPonta: 164,
  buscarReativoAuto: false,
  tarifaReativoEnergia: 0.29098,
  tributarReativos: true,
  pis: 1.0021,
  cofins: 4.6184,
  icms: 19,
  bandeiraAutomatica: false,
  bandeiraManualRkwh: 0.0053016,
  totalFatura: 3156.27,
  retencoesCreditos: 196.11,
});

const DEMANDA = ['demanda_medida_unica_kw', 'demanda_contratada_unica_kw', 'demanda_ponta_kw', 'demanda_fora_ponta_kw', 'demanda_contratada_ponta_kw', 'demanda_contratada_fora_ponta_kw'];

describe('B9 — dados escondidos não vão para a API', () => {
  it('trocar Copel (Verde) para Optante B limpa a demanda', () => {
    const f = trocarModalidade(exemploCopel(), 'optante_b');
    expect(f.demandaMedida).toBeNull();
    expect(f.demandaContratada).toBeNull();
    const corpo = paraConsumidor(f);
    for (const k of DEMANDA) expect(corpo).not.toHaveProperty(k);
  });

  it('Verde não manda campos da Azul nem kVA; Azul não manda a demanda única', () => {
    const verde = paraConsumidor({ ...exemploCopel(), demandaPontaKw: 99, potenciaTransformadoresKva: 75 });
    expect(verde).not.toHaveProperty('demanda_ponta_kw');
    expect(verde).not.toHaveProperty('potencia_transformadores_kva');
    const azul = paraConsumidor({ ...exemploCopel(), modalidadeAtual: 'azul', demandaPontaKw: 6.88, demandaForaPontaKw: 150.65, demandaContratadaPontaKw: 100, demandaContratadaForaPontaKw: 260 });
    expect(azul).not.toHaveProperty('demanda_medida_unica_kw');
    expect(azul.demanda_ponta_kw).toBe(6.88);
  });

  it('nenhuma chamada da análise Optante B leva a demanda antiga (260 kW)', async () => {
    const { chamadas } = instalarApiFake();
    const f = trocarModalidade({ ...exemploCopel(), potenciaTransformadoresKva: 75 }, 'optante_b');
    await executarAnalise({ ...f, potenciaTransformadoresKva: 75 }, null);
    for (const c of chamadas) for (const k of DEMANDA) expect(c.corpo).not.toHaveProperty(k);
  });
});

describe('B10/B11 — Optante B e a comparação com o Grupo A', () => {
  it('sem demanda: Verde e Azul "não avaliado", sem chamada', async () => {
    const { chamadas } = instalarApiFake();
    const a = await executarAnalise(tucurui(), null);
    for (const m of ['Verde', 'Azul']) {
      const x = a.modalidades.find((y) => y.modalidade === m)!;
      expect(x.estado).toBe('nao_avaliado');
      expect(x.motivo).toBe('não avaliado: informe a demanda para comparar com o Grupo A');
    }
    expect(chamadas.some((c) => c.path === '/api/calculo/fatura' && c.params.get('modalidade') !== 'Optante B')).toBe(false);
    // A modalidade atual sempre entra, mesmo que o comparar a marque indisponível.
    expect(a.modalidades.find((y) => y.modalidade === 'Optante B')!.estado).toBe('ok');
    expect(recomendacaoMes(a)).toBeNull();
  });

  it('com demanda informada: Verde/Azul calculadas com ela, e a recomendação nunca custa mais', async () => {
    const { chamadas } = instalarApiFake();
    const a = await executarAnalise({ ...tucurui(), demandaMedida: 20, demandaContratada: 30 }, null);
    const verde = a.modalidades.find((y) => y.modalidade === 'Verde')!;
    expect(verde.estado).toBe('ok');
    expect(verde.selo).toBe('hipotético: demanda informada só para comparar');
    const cAzul = chamadas.find((c) => c.params.get('modalidade') === 'Azul')!;
    expect(cAzul.corpo.demanda_ponta_kw).toBe(20);
    expect(cAzul.corpo.demanda_contratada_fora_ponta_kw).toBe(30);
    const rec = recomendacaoMes(a);
    if (rec) expect(rec.economia).toBeGreaterThan(0);
    const maisBarata = Math.min(...a.modalidades.filter((m) => m.atual).map((m) => m.atual!.total));
    if (maisBarata >= a.faturaAtual.total) expect(rec).toBeNull();
  });
});

describe('B12 — bandeira manual', () => {
  it('manda o valor em R$/kWh; automática = 0', () => {
    expect(bandeiraParaApi(tucurui())).toBe(0.0053016);
    expect(paraConsumidor(tucurui()).bandeira_adicional_r_kwh).toBe(0.0053016);
    expect(bandeiraParaApi({ ...tucurui(), bandeiraAutomatica: true })).toBe(0);
  });
});

describe('B13 — retenções só na conferência', () => {
  const fatura = (total: number): FaturaModalidade =>
    ({ total, com: { linhas: [{ descricao: 'Energia Reativa Excedente Indutiva (Fora Ponta)', categoria: 'REATIVOS', quantidade: 1, tarifa: 1, custo: 9 }] } }) as unknown as FaturaModalidade;

  it('Tucuruí: 3.352,38 − 196,11 = 3.156,27 = impresso; custo continua 3.352,38', () => {
    const c = conferir(tucurui(), fatura(3352.38))!;
    expect(c.liquido).toBeCloseTo(3156.27, 2);
    expect(Math.abs(c.diferenca)).toBeLessThanOrEqual(0.05);
    expect(c.totalCalculado).toBe(3352.38);
    expect(c.reativoNaoCobrado).toBe(false);
  });

  it('sem retenções: conferência com o total técnico; reativo sem excedente é explicado', () => {
    const f = { ...exemploCopel() };
    const semReativo = { total: 9851.96, com: { linhas: [] } } as unknown as FaturaModalidade;
    const c = conferir(f, semReativo)!;
    expect(c.retencoes).toBeNull();
    expect(c.diferenca).toBeCloseTo(-2.97, 2);
    expect(c.reativoNaoCobrado).toBe(true);
  });

  it('retenções nunca vão para a API', async () => {
    const { chamadas } = instalarApiFake();
    await executarAnalise(tucurui(), null);
    expect(chamadas.length).toBeGreaterThan(0);
    for (const c of chamadas) expect(JSON.stringify(c.corpo) + c.params.toString()).not.toContain('196.11');
  });
});

describe('B7 — E-PI com a modalidade', () => {
  it('chama com a modalidade atual e, se a recomendada for outra, com ela também', async () => {
    const plano: PlanejamentoApi = {
      melhor_contrato_atual: 'Verde',
      melhor_demanda_otimizada: 'Azul',
      ganho: { total: 10, demanda: 5, modalidade: 5 },
      modalidades: [
        { modalidade: 'Azul', custo_contrato_atual: 0, custo_demanda_otimizada: 0, dc_atual: [260, 260], dc_otima: [30, 201], pi: null },
        { modalidade: 'Verde', custo_contrato_atual: 0, custo_demanda_otimizada: 0, dc_atual: 260, dc_otima: 201, pi: null },
      ],
      equilibrio: null,
      avisos: [],
    };
    const { chamadas } = instalarApiFake({ planejamento: plano });
    const a = await executarAnalise(exemploCopel(), null);
    const epis = chamadas.filter((c) => c.path === '/api/epi/calcular').map((c) => c.corpo.modalidade);
    expect(epis).toContain('Verde');
    expect(epis).toContain('Azul');
    expect(a.epi.modalidade).toBe('Verde');
    expect(a.epiRecomendada?.modalidade).toBe('Azul');
  });
});

describe('B10 — recomendação determinística', () => {
  const mod = (modalidade: string, total: number | null, estado = 'ok') =>
    ({ modalidade, estado, atual: total === null ? null : { total } }) as never;
  const base = (atual: number, outras: [string, number | null, string?][]) => ({
    modalidadeAtual: 'Optante B' as const,
    faturaAtual: { total: atual } as never,
    modalidades: [mod('Optante B', atual), ...outras.map(([m, t, e]) => mod(m, t, e))],
  });

  it('Optante B R$ 3.333,91 × Verde R$ 17.598,64: a atual já é a mais barata', () => {
    expect(recomendacaoMes(base(3333.91, [['Verde', 17598.64], ['Azul', 53758.4]]))).toBeNull();
  });

  it('só recomenda a mais barata, e a economia é positiva', () => {
    expect(recomendacaoMes(base(1000, [['Verde', 900], ['Azul', 950]]))).toEqual({ modalidade: 'Verde', economia: 100 });
  });

  it('ignora modalidade não avaliada', () => {
    expect(recomendacaoMes(base(1000, [['Verde', null, 'nao_avaliado']]))).toBeNull();
  });
});
