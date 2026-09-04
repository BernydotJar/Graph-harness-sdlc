# Graph Harness SDLC

**Autonomia estruturada sobre um grafo executável, com estado tipado, evidência rastreável e reparo localizado.**

> [English canonical README](../../README.md) · [Español](README.es.md) · [Italiano](README.it.md)

> A documentação em inglês é a versão canônica. Esta tradução pode ficar ligeiramente atrás da versão principal.

`Graph Harness SDLC` é um runtime de execução reutilizável e uma metodologia de engenharia para construir software com agentes de IA sem depender de uma conversa monolítica ou de loops que perdem contexto.

Ele transforma requisitos, tarefas, decisões, resultados de verificação e falhas em nós e relações explícitas que podem ser executados, auditados, retomados e reparados.

**O objetivo não é gerar atividade. O objetivo é terminar o produto.**

## Modelo central

```text
Requisito
  -> Especificação
  -> Aprovação humana
  -> Grafo de tarefas
  -> Executor
  -> Verificação
  -> Evidência
  -> Gate
  -> Done / Reparo localizado
```

O agente não é o centro da arquitetura. Ele é um executor intercambiável operando dentro de um grafo governado por dependências, capacidades, permissões e gates.

## O que fornece

- Spec-Driven Development
- Harness Engineering
- Loop Engineering
- grafos de execução tipados
- estado de execução tipado
- scheduling orientado por dependências
- separação de papéis e capacidades
- gates de aprovação humana
- limites de arquivos e permissões
- evidência verificável
- quality gates determinísticos
- checkpoints persistentes e recovery
- reparo localizado do subgrafo afetado
- decisões e dívida técnica rastreáveis
- execução retomável de sessões longas
- estados terminais explícitos

## Ciclo de execução

```text
Nó READY
    -> Producer
    -> Critic / Red Team
    -> Fixer
    -> Independent Verifier
    -> Release Gate
    -> Evidência persistente
    -> Próximo nó READY
```

Uma feature não está concluída apenas porque o código existe. Ela está concluída quando sua evidência satisfaz todos os gates necessários e o grafo permanece em estado válido.

## Estados terminais

- `COMPLETED` — não resta trabalho de engenharia útil, seguro, desbloqueado e verificável.
- `PARTIAL_WITH_DOCUMENTED_BLOCKERS` — todo o trabalho restante depende exclusivamente de blockers externos documentados, aprovação humana, infraestrutura ou credenciais indisponíveis ou decisões explícitas de produto.
- `SAFETY_STOP` — continuar violaria restrições de segurança, integridade ou gates humanos.

## Princípio orientador

```text
Prompt -> Runtime -> Grafo de execução -> Executores -> Evidência -> Gates -> Estado persistente
```

Cloud Sandbox controla **onde** um agente pode atuar.

Graph Harness SDLC controla **como** o trabalho de engenharia progride e é verificado.

O produto define **qual** capacidade de negócio está sendo construída.
