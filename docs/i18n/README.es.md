# Graph Harness SDLC

**Autonomía estructurada sobre un grafo ejecutable, con estado tipado, evidencia trazable y reparación localizada.**

> [English canonical README](../../README.md) · [Português](README.pt.md) · [Italiano](README.it.md)

> La documentación en inglés es la versión canónica. Esta traducción puede ir ligeramente detrás de la versión principal.

`Graph Harness SDLC` es un runtime de ejecución reutilizable y una metodología de ingeniería para construir software con agentes de IA sin depender de una conversación monolítica ni de loops que pierden contexto.

Convierte requisitos, tareas, decisiones, verificaciones y fallos en nodos y relaciones explícitas que pueden ejecutarse, auditarse, reanudarse y repararse.

**El objetivo no es generar actividad. El objetivo es terminar el producto.**

## Modelo central

```text
Requisito
  -> Especificación
  -> Aprobación humana
  -> Grafo de tareas
  -> Ejecutor
  -> Verificación
  -> Evidencia
  -> Gate
  -> Done / Reparación localizada
```

El agente no es el centro de la arquitectura. Es un ejecutor intercambiable dentro de un grafo gobernado por dependencias, capacidades, permisos y gates.

## Qué proporciona

- Spec-Driven Development
- Harness Engineering
- Loop Engineering
- grafos ejecutables tipados
- estado de ejecución tipado
- scheduling basado en dependencias
- separación de roles y capacidades
- gates de aprobación humana
- límites de archivos y permisos
- evidencia verificable
- quality gates determinísticos
- checkpoints persistentes y recovery
- reparación localizada del subgrafo afectado
- decisiones y deuda técnica trazables
- ejecución reanudable de sesiones largas
- estados terminales explícitos

## Ciclo de ejecución

```text
Nodo READY
    -> Producer
    -> Critic / Red Team
    -> Fixer
    -> Independent Verifier
    -> Release Gate
    -> Evidencia persistente
    -> Siguiente nodo READY
```

Una feature no está completa solamente porque exista código. Está completa cuando su evidencia satisface todos los gates requeridos y el grafo permanece en un estado válido.

## Estados terminales

La ejecución continúa hasta que el repositorio alcanza uno de estos estados:

- `COMPLETED` — no queda trabajo de ingeniería útil, seguro, desbloqueado y verificable.
- `PARTIAL_WITH_DOCUMENTED_BLOCKERS` — todo el trabajo restante depende exclusivamente de blockers externos documentados, aprobaciones humanas, infraestructura o credenciales no disponibles, o decisiones explícitas de producto.
- `SAFETY_STOP` — continuar violaría restricciones de seguridad, integridad o gates humanos.

## Principio guía

```text
Prompt -> Runtime -> Grafo de ejecución -> Ejecutores -> Evidencia -> Gates -> Estado persistente
```

Cloud Sandbox controla **dónde** puede actuar un agente.

Graph Harness SDLC controla **cómo** progresa y se verifica el trabajo de ingeniería.

El producto define **qué** capacidad de negocio se está construyendo.
