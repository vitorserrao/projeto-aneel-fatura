import { afterEach, describe, expect, it, vi } from 'vitest';
import { instalarApiFake } from './apiFake';
import { exemploCopel } from '../formPadrao';
import { executarAnalise } from '../analise';
import { detalharLinhas, pedidoFatura, resumoTributos } from '../cenarios';
import { rotuloLinha } from '../rotulos';
import { lerHistorico } from '../api';
import { calcularSeries, conferirSoma, mesesBase, pedidoMes, pontosCurva, usoPontaHoras, fatorCarga } from '../series';
import type { PlanejamentoApi } from '../api';

afterEach(() => vi.unstubAllGlobals());

const planejamentoFake = (dcAtual = 260, dcOtima = 201): PlanejamentoApi => ({
  melhor_contrato_atual: 'Verde',
  melhor_demanda_otimizada: 'Verde',
  ganho: { total: 0, demanda: 0, modalidade: 0 },
  modalidades: [
    { modalidade: 'Azul', custo_contrato_atual: 0, custo_demanda_otimizada: 0, dc_atual: [dcAtual, dcAtual], dc_otima: [30, dcOtima], pi: null },
    { modalidade: 'Verde', custo_contrato_atual: 0, custo_demanda_otimizada: 0, dc_atual: dcAtual, dc_otima: dcOtima, pi: { anual: 265, mensal: [] } },
  ],
  equilibrio: null,
  avisos: [],
});

describe('B1 — totais por modalidade vêm de /fatura, não de /comparar', () => {
  it('Verde da comparação = Verde da fatura da etapa 2', async () => {
    const { chamadas } = instalarApiFake({ planejamento: planejamentoFake() });
    const a = await executarAnalise(exemploCopel(), null);
    const verde = a.modalidades.find((m) => m.modalidade === 'Verde')!;
    expect(verde.estado).toBe('ok');
    expect(verde.atual!.total).toBeCloseTo(a.faturaAtual.total, 6);
    // /comparar devolveu 10.297,70 para a Verde: esse total não pode aparecer.
    expect(verde.atual!.total).not.toBeCloseTo(10297.7, 0);
    // A fatura da modalidade foi pedida com os mesmos flags da etapa 2.
    const f = chamadas.find((c) => c.path === '/api/calculo/fatura' && c.params.get('modalidade') === 'Verde')!;
    expect(f.params.get('demanda_isenta_icms')).toBe('true');
    expect(f.params.get('demanda_isenta_icms_kw')).toBe('109.35');
    expect(f.params.get('arredondar_centavos')).toBe('true');
    expect(f.params.get('tributar_reativos')).toBe('false');
  });

  it('/comparar só informa indisponíveis e notas', async () => {
    instalarApiFake({ planejamento: planejamentoFake() });
    const form = { ...exemploCopel(), potenciaTransformadoresKva: 300 };
    const a = await executarAnalise(form, null);
    const ob = a.modalidades.find((m) => m.modalidade === 'Optante B')!;
    expect(ob.estado).toBe('indisponivel');
    expect(ob.motivo).toContain('112,5');
    expect(a.notas.map((n) => n.mensagem)).toContain('nota do comparar');
  });

  it('Optante B sem kVA = não avaliado (sem chamada)', async () => {
    const { chamadas } = instalarApiFake({ planejamento: planejamentoFake() });
    const a = await executarAnalise(exemploCopel(), null);
    const ob = a.modalidades.find((m) => m.modalidade === 'Optante B')!;
    expect(ob.estado).toBe('nao_avaliado');
    expect(chamadas.some((c) => c.params.get('modalidade') === 'Optante B')).toBe(false);
  });

  it('sem API: a análise falha com a mensagem e não inventa números', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('Failed to fetch'); }));
    await expect(executarAnalise(exemploCopel(), null)).rejects.toThrow('Failed to fetch');
  });
});

describe('B2 — Azul para unidade Verde', () => {
  it('usa a medida única nos dois postos e a contratada única (D6) e marca hipotético', async () => {
    const { chamadas } = instalarApiFake({ planejamento: planejamentoFake() });
    const a = await executarAnalise(exemploCopel(), null);
    const azul = a.modalidades.find((m) => m.modalidade === 'Azul')!;
    expect(azul.hipotetica).toBe(true);
    const c = chamadas.find((x) => x.path === '/api/calculo/fatura' && x.params.get('modalidade') === 'Azul')!;
    expect(c.corpo.demanda_ponta_kw).toBe(150.65);
    expect(c.corpo.demanda_fora_ponta_kw).toBe(150.65);
    expect(c.corpo.demanda_contratada_ponta_kw).toBe(260);
    expect(c.corpo.demanda_contratada_fora_ponta_kw).toBe(260);
    // A quantidade isenta digitada é da fatura Verde real: não vai para a Azul.
    expect(c.params.has('demanda_isenta_icms_kw')).toBe(false);
  });
});

describe('B3/B4 — tarifa sem tributos e rótulos', () => {
  it('casa as linhas com e sem tributos pela descrição', () => {
    const { fatura } = instalarApiFake();
    const form = exemploCopel();
    const com = pedidoFatura(form, 'Verde', null, true);
    const sem = pedidoFatura(form, 'Verde', null, false);
    const fCom = fatura(com.corpo as never, new URLSearchParams(com.params)).fatura;
    const fSem = fatura(sem.corpo as never, new URLSearchParams(sem.params)).fatura;
    const linhas = detalharLinhas(fCom, fSem, form);
    const te = linhas.find((l) => l.descricao.startsWith('TE ENERGIA PONTA'))!;
    expect(te.tarifaSem).toBe(300);
    expect(te.tarifaCom).toBeCloseTo(390, 6);
    expect(te.pisCofins + te.icms).toBeCloseTo(te.valor - te.valorSem!, 6);
    const isenta = linhas.find((l) => l.isentaIcms)!;
    expect(isenta.icms).toBe(0);
    expect(isenta.rotulo).toBe('Demanda isenta de ICMS');
    const r = resumoTributos(linhas, form);
    expect(r.pis + r.cofins + r.icms).toBeCloseTo(
      linhas.reduce((a, l) => a + l.valor - (l.valorSem ?? l.valor), 0),
      6,
    );
  });

  it('rótulos legíveis e unidades', () => {
    expect(rotuloLinha('TUSD DEMANDA PONTA (com tributos)', 'Verde').rotulo).toBe('Demanda (única)');
    expect(rotuloLinha('TUSD DEMANDA PONTA ISENTA ICMS (com tributos)', 'Verde').rotulo).toBe('Demanda isenta de ICMS');
    expect(rotuloLinha('TUSD DEMANDA FORA PONTA', 'Azul').rotulo).toBe('Demanda fora de ponta');
    expect(rotuloLinha('TE ENERGIA PONTA (com tributos)', 'Verde')).toMatchObject({ rotulo: 'Energia (TE) ponta', unidade: 'MWh' });
    expect(rotuloLinha('TUSD DEMANDA PONTA', 'Verde').unidade).toBe('kW');
  });
});

describe('B5 — séries mensais', () => {
  const form = exemploCopel();
  const { meses } = lerHistorico(form.historico12);

  it('monta o mês como o planejamento (sem reativos/outros, tributos sempre)', () => {
    const base = mesesBase(meses);
    expect(base).toHaveLength(12);
    expect(base[11].dVerde).toBe(150.65); // máx(6,88; 150,65)
    const p = pedidoMes(form, base[11], 'Verde', { unica: 201 });
    expect(p.corpo.demanda_contratada_unica_kw).toBe(201);
    expect(p.corpo.outros_rs).toBeUndefined();
    expect(p.corpo.reativo_energia_fora_ponta_kvArh).toBeUndefined();
    expect(p.params.aplicar_tributos).toBe('true');
    expect(p.params.arredondar_centavos).toBe('false');
    expect(p.params.demanda_isenta_icms_kw).toBeUndefined();
  });

  it('48 faturas mensais (+ ótima sem tributos), soma confere com o planejamento', async () => {
    const { chamadas, fatura } = instalarApiFake();
    const base = mesesBase(meses);
    // Planejamento "verdadeiro" = soma das faturas da API simulada.
    const somaMod = (mod: 'Verde' | 'Azul', c: { unica: number } | { ponta: number; fora: number }) =>
      base.reduce((a, m) => {
        const p = pedidoMes(form, m, mod, c);
        return a + fatura(p.corpo as never, new URLSearchParams(p.params)).fatura.custo_total;
      }, 0);
    const plano = planejamentoFake();
    plano.modalidades[1].custo_contrato_atual = somaMod('Verde', { unica: 260 });
    plano.modalidades[1].custo_demanda_otimizada = somaMod('Verde', { unica: 201 });
    plano.modalidades[0].custo_contrato_atual = somaMod('Azul', { ponta: 260, fora: 260 });
    plano.modalidades[0].custo_demanda_otimizada = somaMod('Azul', { ponta: 30, fora: 201 }) + 5; // diverge

    const progresso: number[] = [];
    const r = await calcularSeries(form, plano, meses, (f) => progresso.push(f));
    expect(chamadas.filter((c) => c.path === '/api/calculo/fatura')).toHaveLength(12 * 2 * 3);
    expect(progresso.at(-1)).toBe(72);
    const verde = r.series.find((s) => s.modalidade === 'Verde')!;
    expect(verde.atual.every((v) => v !== null)).toBe(true);
    const confV = r.conferencias.filter((c) => c.modalidade === 'Verde');
    expect(confV.every((c) => c.ok)).toBe(true);
    const azulOtima = r.conferencias.find((c) => c.modalidade === 'Azul' && c.cenario === 'otima')!;
    expect(azulOtima.ok).toBe(false); // divergência de R$ 5 vira aviso, não é escondida
    expect(azulOtima.diferenca).toBeCloseTo(-5, 6);
  });

  it('conferência: mês faltando nunca vira zero silencioso', () => {
    const c = conferirSoma('Verde', 'atual', [100, null, 50], 150);
    expect(c.ok).toBe(false);
    expect(c.mesesFaltando).toBe(1);
  });
});

describe('B6/B8 — curva e indicadores', () => {
  it('12 a 15 pontos entre 30 kW e 1,3 × máx., incluindo a ótima', () => {
    const p = pontosCurva(210.47, 201, 260);
    expect(p.length).toBeGreaterThanOrEqual(12);
    expect(p.length).toBeLessThanOrEqual(15);
    expect(p[0]).toBe(30);
    expect(p.at(-1)).toBe(Math.ceil(1.3 * 210.47));
    expect(p).toContain(201);
    expect(p).toContain(260);
  });

  it('uso da ponta e fator de carga', () => {
    const [m] = mesesBase(lerHistorico('03/2023; 6,88; 150,65; 55; 9094').meses);
    expect(usoPontaHoras(m)).toBeCloseTo(55 / 6.88, 6);
    expect(fatorCarga(m)).toBeCloseTo(9149 / (150.65 * 31 * 24), 6);
    const [u] = mesesBase(lerHistorico('03/2023; 150,65; 55; 9094').meses);
    expect(usoPontaHoras(u)).toBeNull(); // sem demanda de ponta medida
  });
});

describe('B7 — E-PI', () => {
  it('envia a modalidade e mostra a mensagem da API', async () => {
    const { chamadas } = instalarApiFake({ planejamento: planejamentoFake(), falharEpi: 'TE indisponível para COPEL-DIS A4 Verde' });
    const a = await executarAnalise(exemploCopel(), null);
    const c = chamadas.find((x) => x.path === '/api/epi/calcular')!;
    expect(c.corpo.modalidade).toBe('Verde');
    expect(c.corpo.data_referencia).toBe('2023-03-15');
    expect(a.epi.erro).toBe('TE indisponível para COPEL-DIS A4 Verde');
  });
});

describe('faixa boa da curva', () => {
  it('interpola as bordas entre os pontos vizinhos', async () => {
    const { faixaBoa } = await import('../series');
    const f = faixaBoa([
      { dc: 180, custo: 1100 },
      { dc: 200, custo: 1000 },
      { dc: 220, custo: 1050 },
    ]);
    // 1005 é cruzado a 1/20 do caminho 200→180 (199) e a 1/10 do caminho 200→220 (202).
    expect(f).toEqual([199, 202]);
  });
});
