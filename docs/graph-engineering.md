# Graph Engineering

Graph Harness SDLC representa el trabajo como dos grafos relacionados.

## Product knowledge graph

Contiene entidades persistentes del producto:

- Requirement
- Feature
- Component
- API
- Schema
- Decision
- Risk
- Test
- Eval
- Commit
- Pull Request

Relaciones recomendadas:

```text
DEPENDS_ON
IMPLEMENTS
VERIFIED_BY
EVIDENCED_BY
BLOCKED_BY
SUPERSEDES
AFFECTS
REPAIRS
```

## Execution graph

Contiene unidades operativas:

- Task
- Agent
- Tool
- Capability
- Gate
- HumanApproval
- Artifact
- Failure
- Checkpoint

Un nodo puede ejecutarse cuando sus dependencias están satisfechas, sus locks están libres, sus gates previos han pasado y existe un ejecutor con la capacidad requerida.

## Estado y eventos

La fuente canónica debe evolucionar hacia eventos append-only y un estado derivado:

```text
events.jsonl -> graph state -> generated projections
```

Los ledgers, reportes y documentos de progreso son proyecciones; no deben competir como fuentes de verdad independientes.

## Reparación localizada

Cuando un gate falla:

1. identifica el nodo y la evidencia defectuosa;
2. calcula descendientes afectados;
3. invalida únicamente ese subgrafo;
4. crea nodos de reparación;
5. vuelve a ejecutar los gates necesarios;
6. conserva intacta la evidencia no afectada.

Este modelo reduce reinicios amplios, pérdida de contexto y retrabajo innecesario.
