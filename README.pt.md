<div align="center">

<img src="assets/graph-harness-cats.svg" alt="Três gatos conectados como um grafo executável de entrega de software" width="900" />

# Graph Harness SDLC

**Autonomia estruturada sobre um grafo executável de entrega de software.**

[English — canônico](README.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md)

</div>

Graph Harness SDLC é um runtime de execução e uma metodologia de engenharia para programas autônomos e duradouros de desenvolvimento de software.

Ele transforma a entrega de software de uma sequência de prompts isolados em um grafo executável persistente, composto por estado tipado, dependências explícitas, quality gates, evidência rastreável e reparo localizado.

**O inglês é o idioma canônico da documentação.** Esta tradução amplia o acesso, enquanto identificadores normativos, esquemas e contratos do runtime permanecem em inglês.

## Princípio central

> O grafo de execução é a fonte da verdade. Os agentes são executores intercambiáveis.

Uma feature não está concluída apenas porque existe código. Ela só está completa quando sua evidência satisfaz todos os gates exigidos e o grafo permanece em um estado válido.

## O que fornece

- Grafos executáveis de desenvolvimento
- Estado de execução tipado
- Agendamento consciente de dependências
- Checkpoints persistentes
- Separação entre producer, critic, fixer e verifier
- Quality gates determinísticos
- Conclusão respaldada por evidência
- Reparo localizado
- Gates de aprovação humana
- Execução retomável de sessões longas
- Estados terminais explícitos

## Ciclo de execução

```text
Nó pronto
    ↓
Producer
    ↓
Critic / Red Team
    ↓
Fixer
    ↓
Verifier independente
    ↓
Release Gate
    ↓
Evidência persistente
    ↓
Próximo nó pronto
```

## Objetivo

O objetivo não é gerar atividade.

**O objetivo é terminar o produto.**

A execução continua até que o repositório alcance um dos três estados terminais do programa:

- `COMPLETED`
- `PARTIAL_WITH_DOCUMENTED_BLOCKERS`
- `SAFETY_STOP`

Esses resultados pertencem ao programa completo e são distintos de estados de nó como `done`, `blocked` e `repair_required`. Consulte [Terminal states](docs/terminal-states.md).

## Modelo do runtime

Um repositório consumidor fornece um grafo `graph-harness.project.v1`, um ledger append-only `graph-harness.event.v1` e adaptadores de domínio fixados a uma revisão específica do framework. O runtime deriva `graph-harness.state.v1` e governa transições, dependências, evidências, gates, checkpoints e reparo localizado.

O runtime não concede autoridade para merge, release, deployment, gastos, alteração de segredos ou efeitos externos. Essas decisões permanecem sob gates humanos ou do repositório consumidor.

## Início rápido

```sh
./init.sh
```

## Documentação

- [Índice da documentação](docs/README.md)
- [Conceitos](docs/concepts.md)
- [Arquitetura do runtime](docs/runtime-architecture.md)
- [Arquitetura do sistema](docs/system-architecture.md)
- [Tutoriais](docs/tutorials.md)
- [Exemplos](examples/)
- [Referência](docs/reference.md)

Graph Harness SDLC não é uma aplicação nem uma coleção de prompts. É o sistema operacional reutilizável de execução que repositórios consumidores usam para entregar software por meio de um grafo governado.
