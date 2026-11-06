/**
 * Executa tarefas assíncronas com limite de simultaneidade (padrão 6) e
 * avisa o progresso. Falha de uma tarefa não interrompe as outras: o
 * resultado traz `ok`/`erro` por posição, na mesma ordem das tarefas.
 */
export type ResultadoTarefa<T> = { ok: true; valor: T } | { ok: false; erro: unknown };

export async function executarComLimite<T>(
  tarefas: (() => Promise<T>)[],
  limite = 6,
  aoProgredir?: (feitas: number, total: number) => void,
): Promise<ResultadoTarefa<T>[]> {
  const resultados: ResultadoTarefa<T>[] = new Array(tarefas.length);
  let proxima = 0;
  let feitas = 0;
  aoProgredir?.(0, tarefas.length);
  async function trabalhador() {
    while (proxima < tarefas.length) {
      const i = proxima;
      proxima += 1;
      try {
        resultados[i] = { ok: true, valor: await tarefas[i]() };
      } catch (erro) {
        resultados[i] = { ok: false, erro };
      }
      feitas += 1;
      aoProgredir?.(feitas, tarefas.length);
    }
  }
  const n = Math.max(1, Math.min(limite, tarefas.length));
  await Promise.all(Array.from({ length: n }, trabalhador));
  return resultados;
}
