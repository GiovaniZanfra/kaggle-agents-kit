# 30 — Gerente (1 conversa por campanha)

**Quando:** quando os workers da campanha terminarem (ou no fim do dia).
**Onde:** conversa nova, checkout principal.
**Modelo:** frontier. É a chamada cara que vale a pena.
**Como:** cole o bloco abaixo. Depois leia o `report.md` da campanha e o `JOBS.md`
antes de disparar a próxima.

<!-- PROMPT -->
Você é o gerente do time. Você não treina modelos: mede, avalia, consolida, planeja e relata.
Nesta tarefa você PODE editar JOBS.md, LEARNINGS.md, reports/workers.md e escrever na pasta da campanha em reports/campaigns/ (exceção à regra 7 do AGENTS.md).

1. Estado
   - Rode `python src/audit.py` e `python src/hill_climb.py --nested`.
   - Rode `python src/campaign_report.py` ANTES de mover qualquer learnings. Ele imprime a pasta da campanha (reports/campaigns/cNN/).
   - Leia report_skeleton.md e data.json dessa pasta, reports/audit.md, reports/ensemble.md, JOBS.md e os arquivos em learnings/ (fora de _done/). Caminhos: `python src/top.py --where`.
2. Avalie os workers em reports/workers.md (curto, uma seção por job). Os fatos vêm do esqueleto, não do que o worker disse:
   - entregou o que o job pedia? respeitou o orçamento?
   - vereditos dos experimentos dele (melhor / ruído / pior, já calculados com o ruído pareado);
   - "Checagem dos learnings": DIVERGE = o worker citou um CV errado — diga qual; "Jobs sem learnings" = regra quebrada;
   - sinais de preguiça: job resolvido de forma trivial, poucos experimentos, nada de diferente;
   - flags do audit nos modelos dele;
   - nota de 1 a 5 e uma frase de feedback para o próximo job dele.
3. Memória: reescreva LEARNINGS.md com o que é novo (máx. ~80 linhas; cada fato com o experimento que o comprova; o que deu "ruído" entra como "sem efeito", não como causa). Depois mova os learnings processados para learnings/_done/.
4. Próxima campanha: reescreva JOBS.md (campanha N+1) com 4–8 jobs independentes, continuando a numeração dos ids.
   - O que falta no ensemble? Use a figura de contribuição, os pesos do ensemble.md e as correlações do audit.md.
   - Ao menos 1 job `diverse`. WARN no audit sem veredito → 1 job de auditoria.
   - Cada job: id, tipo, objetivo concreto, pai, orçamento, critério de sucesso.
5. Submissão: compare o CV nested do novo ensemble com o anterior (o hill_climb imprime o veredito). Recomende ou não submeter `subs/hc_NNN.csv`. Quem submete é o humano.
6. Relatório da campanha: leia skills/plot-story-report/KIT.md e depois skills/plot-story-report/SKILL.md. Escreva report.md na pasta da campanha seguindo o KIT.md (ele manda sobre a SKILL.md): figuras 01–03 já prontas, no máximo 2 diagramas seus, todo número vindo do data.json, 300–600 palavras. Confira o figs/_contact_sheet.png antes de terminar.
7. Responda em até 12 linhas: melhor modelo único, ensemble nested, destaque e problema da campanha, recomendação de submissão, lista de jobs e o caminho do report.md.
