# Como usar a plot-story-report dentro deste kit

`SKILL.md` nesta pasta é uma cópia da skill `plot-story-report` (15/10/2026). Se a
skill original mudar, copie de novo. Ela fica aqui, fora de `.claude/skills/`, de
propósito: assim nenhum agente a dispara sozinho ao escrever um learnings.
Só o **gerente** usa, uma vez por campanha, a partir de `prompts/30_manager.md`.

As regras abaixo têm prioridade sobre o `SKILL.md` quando os dois divergirem.

## O que muda em relação à skill

1. **As figuras de dados já existem.** `python src/campaign_report.py` gera
   `figs/01_deltas.png`, `02_trajetoria.png` e `03_contribuicao.png` a partir do
   registry. Use essas. Não redesenhe gráfico de números: o ponto é que os números
   não passem pelas mãos de um agente.
2. **Diagramas são opcionais**, no máximo 2, para explicar um *mecanismo* (como uma
   feature é construída, como um stack está montado). Use `src/plotkit.py` (já está
   no repo, idêntico ao da skill) e salve na mesma pasta `figs/` com prefixo `04_`, `05_`.
   Diagrama não carrega número que não esteja no `data.json`.
3. **Todo número do texto vem do `data.json`** e cita o experimento:
   "xgb_j4_002 subiu 0,0007 sobre o pai (±0,0004)". Nada de número de memória ou
   tirado do learnings de um worker.
4. **Ruído é ruído.** Experimento com veredito `ruído` não ganha explicação causal.
   Escreva "dentro do ruído" e siga. Explicação de "por que funcionou" só para
   `melhor`, e marcada como hipótese se não houver um experimento que a isole.
5. **Learnings dos workers são relato, não evidência.** Use para contar o que cada
   job tentou. Se a tabela "Checagem dos learnings" do esqueleto mostrar `DIVERGE`,
   diga isso no relatório, com o nome do job.
6. **Os títulos calculados ficam.** Os títulos das figuras 01–03 saíram dos dados.
   Pode reescrever a frase, mas não pode mudar o que ela afirma.

## Formato

- Público: `peers` (você mesmo). Português. **300–600 palavras.**
- Esqueleto (adaptado do template da skill):

```markdown
# Campanha cNN: <uma frase com o resultado>

<linha de resultado do esqueleto, reescrita em 1–2 frases>

## <título da fig. 01>
![](figs/01_deltas.png)
<2–3 frases: o que separou os "melhor" do resto>

## <título da fig. 02>
![](figs/02_trajetoria.png)
<1–2 frases: o teto mexeu? o ensemble acompanhou?>

## <título da fig. 03>
![](figs/03_contribuicao.png)
<1–2 frases: quem trouxe diversidade>

## O que aprendemos
<2–4 frases honestas: o que não funcionou, divergências nos learnings, flags do audit>

## Próxima campanha
<os jobs em uma lista curta, com o porquê de cada um>

**Detalhes, para os curiosos:** <tabela de experimentos do esqueleto, colada como está>
```

- Antes de entregar: abra `figs/_contact_sheet.png` (e os diagramas que você
  fez), confira os números do texto contra o `data.json` e leia só os títulos
  em ordem — eles precisam contar a campanha sozinhos.
