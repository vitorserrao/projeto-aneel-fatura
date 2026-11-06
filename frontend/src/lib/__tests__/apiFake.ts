/**
 * API simulada para os testes (tarifas fictícias, sem banco).
 *
 * /fatura: TE/TUSD por energia + demanda faturável (máx. medida/contratada),
 * com fator de tributos 1,3 quando aplicar_tributos=true, e a parcela isenta
 * de ICMS separada quando demanda_isenta_icms=true (fator 1,1).
 * /comparar devolve um total DIFERENTE para a Verde, como o bug B1 real.
 */
import { vi } from 'vitest';

export interface Chamada {
  path: string;
  params: URLSearchParams;
  corpo: Record<string, number | string>;
}

const TE = 300; // R$/MWh
const TUSD = 100; // R$/MWh
const DEM = 20; // R$/kW

function fatura(corpo: Record<string, number | string>, params: URLSearchParams) {
  const mod = params.get('modalidade') ?? 'Verde';
  const trib = params.get('aplicar_tributos') === 'true';
  const isenta = params.get('demanda_isenta_icms') === 'true';
  const f = trib ? 1.3 : 1;
  const fIsenta = trib ? 1.1 : 1;
  const sufixo = trib ? ' (com tributos)' : '';
  const eP = Number(corpo.consumo_ponta_kwh ?? 0) / 1000;
  const eF = Number(corpo.consumo_fora_ponta_kwh ?? 0) / 1000;
  const linhas: { descricao: string; categoria: string; quantidade: number; tarifa: number; custo: number }[] = [];
  const add = (d: string, q: number, t: number, fator = f) =>
    linhas.push({ descricao: d + sufixo, categoria: 'TARIFA', quantidade: q, tarifa: t * fator, custo: q * t * fator });
  add('TE ENERGIA PONTA', eP, TE);
  add('TE ENERGIA FORA PONTA', eF, TE);
  add('TUSD ENERGIA PONTA', eP, TUSD);
  add('TUSD ENERGIA FORA PONTA', eF, TUSD);
  const postos: [string, number, number][] =
    mod === 'Verde'
      ? [['PONTA', Number(corpo.demanda_medida_unica_kw ?? 0), Number(corpo.demanda_contratada_unica_kw ?? 0)]]
      : [
          ['PONTA', Number(corpo.demanda_ponta_kw ?? 0), Number(corpo.demanda_contratada_ponta_kw ?? 0)],
          ['FORA PONTA', Number(corpo.demanda_fora_ponta_kw ?? 0), Number(corpo.demanda_contratada_fora_ponta_kw ?? 0)],
        ];
  for (const [posto, med, cont] of postos) {
    const fat = Math.max(med, cont);
    if (isenta && cont > med) {
      add(`TUSD DEMANDA ${posto}`, med, DEM);
      add(`TUSD DEMANDA ${posto} ISENTA ICMS`, cont - med, DEM, fIsenta);
    } else add(`TUSD DEMANDA ${posto}`, fat, DEM);
    if (cont > 0 && med > 1.05 * cont) {
      linhas.push({ descricao: 'Ultrapassagem de demanda', categoria: 'ULTRAPASSAGEM', quantidade: med - cont, tarifa: 40, custo: (med - cont) * 40 });
    }
  }
  const outros = Number(corpo.outros_rs ?? 0);
  if (outros > 0) linhas.push({ descricao: 'Outros valores', categoria: 'OUTROS', quantidade: 1, tarifa: outros, custo: outros });
  const total = linhas.reduce((a, l) => a + l.custo, 0);
  return {
    fatura: { modalidade: mod, base_tarifaria: 'Tarifa de Aplicação', linhas, custo_tarifas: total, custo_total: total, aplicar_tributos: trib, tarifas_nao_mapeadas: 0 },
    notas: [],
  };
}

export function instalarApiFake(opcoes: { planejamento?: unknown; falharEpi?: string } = {}) {
  const chamadas: Chamada[] = [];
  const fetchFake = vi.fn(async (url: string, init?: { body?: string }) => {
    const u = new URL(url);
    const corpo = init?.body ? JSON.parse(init.body) : {};
    chamadas.push({ path: u.pathname, params: u.searchParams, corpo });
    const json = (o: unknown, status = 200) =>
      ({ ok: status < 400, status, json: async () => o, text: async () => JSON.stringify(o) }) as unknown as Response;
    if (u.pathname === '/api/calculo/fatura') return json(fatura(corpo, u.searchParams));
    if (u.pathname === '/api/calculo/comparar') {
      return json({
        comparacao: {
          disponiveis: [{ ...fatura(corpo, new URLSearchParams({ modalidade: 'Verde', aplicar_tributos: 'true' })).fatura, custo_total: 10297.7 }],
          indisponiveis: [{ modalidade: 'Optante B', motivo: 'Potência dos transformadores acima de 112,5 kVA' }],
          melhor: 'Verde',
        },
        notas: [{ tipo: 'info', mensagem: 'nota do comparar' }],
      });
    }
    if (u.pathname === '/api/planejamento/comparar') {
      return opcoes.planejamento ? json(opcoes.planejamento) : json({ detail: 'sem planejamento' }, 422);
    }
    if (u.pathname === '/api/epi/calcular') {
      if (opcoes.falharEpi) return json({ detail: opcoes.falharEpi }, 400);
      return json({ pi: 265, modalidade: String(corpo.modalidade).toUpperCase(), bandeira_r_mwh: 0, e_mwh: 9.149, c_te: 1, c_e_acr: 1, custos_acl: 0, base_acl: 11.49, aviso: null });
    }
    return json({ detail: 'rota desconhecida' }, 404);
  });
  vi.stubGlobal('fetch', fetchFake);
  return { chamadas, fetchFake, fatura };
}
