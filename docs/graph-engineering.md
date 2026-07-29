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

La ejecución usa contratos versionados y estado derivado:

```text
graph-harness.project.v1 + graph-harness.event.v1 JSONL
  -> graph-harness.state.v1
  -> generated projections
```

Cada evento conserva secuencia, actor, revisión de nodo y una cadena SHA-256. La revisión aumenta cuando un fallo invalida el nodo; por ello la evidencia anterior permanece auditable pero deja de satisfacer gates actuales.

Los ledgers, reportes y documentos de progreso son proyecciones; no deben competir como fuentes de verdad independientes.

## Reparación localizada

Cuando un gate falla:

1. identifica el nodo y la evidencia defectuosa;
2. calcula descendientes afectados;
3. invalida únicamente ese subgrafo;
4. incrementa la revisión de cada nodo afectado;
5. registra un plan de reparación;
6. vuelve a ejecutar los gates necesarios;
7. conserva intacta la evidencia no afectada.

Este modelo reduce reinicios amplios, pérdida de contexto y retrabajo innecesario.
