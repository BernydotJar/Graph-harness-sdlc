<div align="center">

<img src="assets/graph-harness-cats.svg" alt="Tres gatos conectados como un grafo ejecutable de entrega de software" width="900" />

# Graph Harness SDLC

**Autonomía estructurada sobre un grafo ejecutable de entrega de software.**

[English — canónico](README.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md)

</div>

Graph Harness SDLC es un runtime de ejecución y una metodología de ingeniería para programas de desarrollo de software autónomos y de larga duración.

Convierte la entrega de software, antes fragmentada en prompts aislados, en un grafo ejecutable persistente compuesto por estado tipado, dependencias explícitas, quality gates, evidencia trazable y reparación localizada.

**El inglés es el idioma canónico de la documentación.** Esta traducción facilita el acceso, pero los identificadores normativos, esquemas y contratos del runtime permanecen en inglés.

## Principio central

> El grafo de ejecución es la fuente de verdad. Los agentes son ejecutores intercambiables.

Una feature no está terminada porque exista código. Solo está completa cuando su evidencia satisface todos los gates requeridos y el grafo conserva un estado válido.

## Qué proporciona

- Grafos ejecutables de desarrollo
- Estado de ejecución tipado
- Programación consciente de dependencias
- Checkpoints persistentes
- Separación entre producer, critic, fixer y verifier
- Quality gates determinísticos
- Finalización respaldada por evidencia
- Reparación localizada
- Gates de aprobación humana
- Ejecución reanudable de sesiones largas
- Estados terminales explícitos

## Ciclo de ejecución

```text
Nodo listo
    ↓
Producer
    ↓
Critic / Red Team
    ↓
Fixer
    ↓
Verifier independiente
    ↓
Release Gate
    ↓
Evidencia persistente
    ↓
Siguiente nodo listo
```

## Objetivo

El objetivo no es generar actividad.

**El objetivo es terminar el producto.**

La ejecución continúa hasta alcanzar uno de tres estados terminales del programa:

- `COMPLETED`
- `PARTIAL_WITH_DOCUMENTED_BLOCKERS`
- `SAFETY_STOP`

Estos resultados pertenecen al programa completo y son distintos de estados de nodo como `done`, `blocked` y `repair_required`. Consulte [Estados terminales](docs/terminal-states.md).

## Modelo del runtime

Un repositorio consumidor aporta un grafo `graph-harness.project.v1`, un ledger append-only `graph-harness.event.v1` y adaptadores de dominio fijados a una revisión específica del framework. El runtime deriva `graph-harness.state.v1` y gobierna transiciones, dependencias, evidencia, gates, checkpoints y reparación localizada.

El runtime no concede autoridad para merge, release, deployment, gasto, cambios de secretos ni efectos externos. Esas decisiones siguen bajo gates humanos o del repositorio consumidor.

## Inicio rápido

```sh
./init.sh
```

```sh
python3 -m graph_harness \
  --project graph-harness.project.json \
  --events graph-harness.events.jsonl \
  validate
```

## Documentación

- [Índice documental](docs/README.md)
- [Conceptos](docs/concepts.md)
- [Arquitectura del runtime](docs/runtime-architecture.md)
- [Arquitectura del sistema](docs/system-architecture.md)
- [Tutoriales](docs/tutorials.md)
- [Ejemplos](examples/)
- [Referencia](docs/reference.md)

Graph Harness SDLC no es una aplicación ni una colección de prompts. Es el sistema operativo reutilizable de ejecución que los repositorios consumidores utilizan para entregar software mediante un grafo gobernado.
