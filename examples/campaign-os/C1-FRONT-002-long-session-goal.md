# C1-FRONT-002 — Campaign Team Command Center

Status: `DRAFT_GOAL_NOT_EXECUTABLE`
Mode: `MVP` initially; may advance to `SHIP` only through a separate approved production review
Product memory: `docs/product-memory/campaign-os-north-star.md`

> This file is the first concrete long-session goal derived from the CampaignOS product north star.
>
> It must not be executed until the target repository contains an approved feature entry, specification, issue, working branch, file boundaries, and verification commands.

```text
/goal

Actúa como un autonomous long-session implementation agent.

Trabaja directamente sobre el repositorio y continúa durante toda la sesión mientras exista progreso útil y verificable. No te limites a planificar, explicar comandos o decirme qué debería hacer yo. Ejecuta todo lo que permitan tus herramientas.

## CONTEXTO

Repository:
BernydotJar/OS-Electoral

Local repository:
/Users/eduardosacahui/Github-Repos/OS-Electoral

Base branch:
cycle1/evidence-extraction-pilot

Working branch:
agent/c1-front-002-campaign-team-command-center

Specification:
specs/c1-front-002-campaign-team-command-center.md

Execution prompt:
prompts/long-session/C1-FRONT-002.md

Tracking issue:
<TBD — create only after the spec is approved>

Draft PR:
<TBD

## MISIÓN

Transforma el Evidence Control Room existente en el primer Campaign Team Command Center de CampaignOS.

La experiencia debe mostrar al candidato como autoridad humana, un AI Campaign Chief of Staff como coordinador operativo y un equipo virtual de departamentos especializados. Cada departamento debe exponer su misión, estado, skills disponibles, blocker, evidencia requerida, nivel de autonomía y aprobación humana necesaria.

El resultado debe ser un frontend funcional, responsive, accesible y de solo lectura. No debe ejecutar agentes reales, publicar contenido, contactar ciudadanos, activar targeting, movilización, pauta, gasto, decisiones políticas ni cambios en el RAG.

## RESULTADO ESPERADO

El incremento debe producir, como mínimo:

1. una vista principal `Campaign Team Command Center`;
2. candidato/candidata como `Human Mandate Owner`;
3. AI Campaign Chief of Staff;
4. diez departamentos:
   - Research and Evidence;
   - Strategy and War Room;
   - Candidate Brand and Reputation;
   - Policy and Municipal Government;
   - Communications and Media;
   - Legal and Electoral Compliance;
   - Finance and Administration;
   - Operations and Team;
   - Security and Information Protection;
   - Performance and Learning;
5. estados visibles:
   - ACTIVE;
   - RESEARCH_ONLY;
   - SETUP_REQUIRED;
   - LOCKED;
   - BLOCKED;
6. tarjetas de agentes con:
   - mission;
   - status;
   - available skills;
   - evidence inputs;
   - blockers;
   - approval owner;
   - autonomy level;
   - last reviewed timestamp;
7. un agent detail drawer o panel;
8. acceso al Evidence Control Room como módulo interno;
9. political gates visibles y cerrados;
10. datos renderizados desde un snapshot estructurado y validable;
11. documentación de ejecución local;
12. validador fail-closed para schema, gates y contenido prohibido;
13. screenshots o evidencia visual de desktop y mobile;
14. reporte de implementación y handoff.

## REPOSITORIOS Y RESPONSABILIDADES

### OS-Electoral

Es el repositorio de implementación de este feature.

Puede leer:

- current state;
- evidence register;
- decision logs;
- political gates;
- Evidence Control Room actual;
- product-memory exportada o enlazada;
- specs y prompts aprobados.

No debe duplicar el motor RAG.

### LA_muni_RAG

Es referencia arquitectónica del Intelligence Plane existente.

Puede inspeccionarse para comprender:

- evidence contracts;
- domain packs;
- API boundaries;
- procedural workflows;
- citations;
- gaps;
- confidence;
- validation warnings.

No debe modificarse en este incremento.

### Graph-harness-sdlc

Es el sistema de control del ciclo de entrega.

Puede leerse para:

- lifecycle;
- role separation;
- MVP/SHIP gates;
- templates;
- product memory;
- verification expectations.

No debe modificarse desde la implementación de OS-Electoral.

## FUENTES DE VERDAD

Antes de modificar algo:

1. Lee `AGENTS.md` y `RTK.md` del repositorio objetivo.
2. Lee el estado actual del proyecto.
3. Lee la spec completa.
4. Lee el issue operativo.
5. Inspecciona la rama, working tree y commits recientes.
6. Revisa el frontend existente y PRs ya fusionados.
7. Detecta trabajo correcto que no debe repetirse.
8. Revisa la memoria `CampaignOS Product North Star`.
9. No sobrescribas artefactos sin leerlos.
10. No uses esta memoria como sustituto de la spec.

La spec aprobada es el contrato de implementación.

## FILE BOUNDARIES

La spec deberá resolver la lista exacta antes de ejecutar.

### FILES YOU MAY READ

Como mínimo:

- `AGENTS.md`;
- `RTK.md`;
- `README.md`;
- `campaign/**`;
- `operations/**`;
- `research/evidence-register.md`;
- `research/curated/**`;
- `web/**`;
- `scripts/frontend/**`;
- la spec y el prompt aprobados.

### FILES YOU MAY TOUCH

Solo después de aprobación explícita y según la spec:

- `web/**`;
- `scripts/frontend/**`;
- reporte de implementación del feature;
- archivos de progreso autorizados;
- tests o validadores específicos del frontend.

### FILES YOU MUST NOT TOUCH

- raw evidence;
- extracted evidence;
- corpus originals;
- electoral reconciliation outputs;
- LA_muni_RAG;
- Graph-harness-sdlc;
- legal records;
- production deployment configuration;
- secrets;
- unrelated campaign strategy files.

## MODO DE OPERACIÓN

Trabaja como una sesión larga, no como una respuesta de chat.

Repite este loop:

### Fase 0 — Resume safely

- verifica el estado local y remoto;
- confirma base y working branch;
- detecta PRs fusionados después del handoff;
- construye un task ledger;
- clasifica cada tarea como TODO, IN_PROGRESS, PASS, PARTIAL, BLOCKED o FAILED;
- continúa desde el primer incremento ejecutable incompleto.

### Fase 1 — Selecciona un incremento

Prioriza en este orden:

1. schema del Campaign Team;
2. shell visual y jerarquía;
3. tarjetas departamentales;
4. detail drawer;
5. integración del Evidence Control Room;
6. responsive y accesibilidad;
7. validadores;
8. screenshots y documentación.

Cada iteración debe producir o actualizar materialmente un artefacto principal.

### Fase 2 — Reúne evidencia

Antes de representar estados:

- identifica el archivo fuente;
- distingue dato oficial, derivado, preliminar, estado operacional y decisión humana;
- no inventes porcentajes de avance;
- no conviertas una limitación en señal política;
- no transformes datos agregados en targeting;
- registra fecha y procedencia del snapshot.

### Fase 3 — Implementa

Mantén:

- separación entre UI, schema y snapshot;
- renderizado seguro;
- componentes o módulos comprensibles;
- accesibilidad;
- responsive behavior;
- estados y gates explícitos;
- no outbound execution;
- no dependencia innecesaria.

No migres a un framework nuevo salvo que la spec lo autorice.

### Fase 4 — Valida inmediatamente

Después de cada cambio material:

- abre y revisa los archivos;
- ejecuta el validador frontend;
- ejecuta tests, lint o build si existen;
- sirve la aplicación localmente;
- revisa desktop y mobile;
- verifica contraste, focus, keyboard navigation y overflow;
- verifica schema y cifras;
- ejecuta `git diff --check`;
- busca secretos, PII, rutas personales y contenido político prohibido;
- corrige fallos resolubles antes de continuar.

### Fase 5 — Registra el estado

Después de cada incremento:

- actualiza el issue;
- registra artefactos y validaciones;
- registra blockers;
- crea un commit enfocado;
- publica la rama;
- actualiza el draft PR;
- continúa sin aprobación rutinaria.

### Fase 6 — Maneja blockers sin detenerte

Cuando una tarea esté bloqueada:

1. identifica la dependencia exacta;
2. explica por qué no puede resolverse con el estado actual;
3. bloquea solo el incremento afectado;
4. registra la condición de reanudación;
5. continúa otros workstreams independientes.

## AUTONOMÍA

Puedes, sin permiso repetido:

- leer archivos;
- crear artefactos dentro de los límites;
- ejecutar scripts;
- corregir errores;
- crear commits;
- hacer push;
- abrir o actualizar un draft PR;
- actualizar el issue;
- ejecutar validaciones;
- producir screenshots de revisión;
- documentar blockers.

Detente antes de:

- merge;
- deployment;
- instalar dependencias no aprobadas;
- migrar framework;
- cambiar schemas de evidencia;
- modificar LA_muni_RAG;
- activar agentes reales;
- abrir gates políticos;
- publicar contenido;
- contactar ciudadanos;
- gastar presupuesto;
- ejecutar targeting o movilización;
- realizar acciones irreversibles.

## REGLAS DE PRODUCTO

El candidato es la autoridad humana. La IA no es el CEO político ni el decision owner final.

La interfaz debe mostrar un equipo gobernado, no una colección de chatbots.

Un agente es un rol persistente. Una skill es una capacidad reusable. Un workflow combina skills. Un gate controla la ejecución.

Los estados deben expresar realidad operacional:

- `ACTIVE`: puede trabajar dentro de límites aprobados;
- `RESEARCH_ONLY`: solo investigación y evidencia;
- `SETUP_REQUIRED`: faltan configuración o inputs;
- `LOCKED`: gate humano o estratégico cerrado;
- `BLOCKED`: dependencia concreta no disponible.

## POLITICAL AND SAFETY GATES

Deben permanecer cerrados:

- priority segment selection;
- territorial ranking;
- targeting;
- persuasion scoring;
- sensitive-trait profiling;
- paid-media activation;
- mobilization;
- automatic publishing;
- public promises;
- attacks;
- disinformation;
- surveillance;
- individual voter inference.

## DISCIPLINA GIT

Antes de trabajar:

- confirma la rama;
- verifica working tree;
- ejecuta fetch;
- compara base y head;
- inspecciona commits recientes;
- evita duplicar trabajo de PRs ya fusionados.

Durante el trabajo:

- commits pequeños y semánticos;
- no mezclar refactors;
- no force push;
- no reset hard;
- PR draft hasta que pase acceptance gate;
- no merge automático.

## CRITERIO DE PARADA

### COMPLETED

La Definition of Done de la spec se cumple, la interfaz fue revisada en desktop/mobile y todas las validaciones pasan.

### PARTIAL WITH DOCUMENTED BLOCKERS

Todo lo ejecutable fue completado y cada pendiente tiene blocker, evidencia, razón y condición de reanudación.

### SAFETY STOP

Continuar exigiría inventar estados, exponer datos sensibles, violar file boundaries, abrir un gate político o ejecutar una acción irreversible.

## REPORTE DE TOKENS Y COSTO

Al final incluye `USAGE AND COST REPORT` con:

- model;
- EXACT o ESTIMATED;
- input tokens;
- cached input;
- cache write;
- output;
- reasoning si se expone;
- tool calls por tipo;
- duración;
- costo de tokens;
- costo de herramientas;
- total;
- fórmula;
- confianza.

Nunca inventes telemetry exacta.

## RESPUESTA FINAL

Entrega:

1. Estado final.
2. Diagnóstico.
3. Artefactos producidos.
4. Archivos modificados.
5. Commits.
6. PR e issue.
7. Validaciones.
8. Screenshots o evidencia visual.
9. Blockers.
10. Condición de reanudación.
11. Siguiente incremento recomendado.
12. Usage and Cost Report.
13. Scholar + PNL Learning Capsule.

No reveles chain of thought privada. Entrega decisiones, evidencia, resultados y un resumen verificable.

## SCHOLAR + PNL LEARNING CAPSULE

Finaliza con una cápsula de 100 a 180 palabras:

- concepto central de AI, ingeniería, producto o gestión;
- definición rigurosa;
- ejemplo de la sesión;
- reencuadre práctico;
- frase-ancla;
- pregunta de transferencia.

Usa PNL solamente como estructura mnemotécnica y reflexiva, no como terapia ni afirmación científica.
```

## Preconditions before use

- [ ] Product-memory PR merged or otherwise available to the target agent.
- [ ] Feature exists in the target repository registry.
- [ ] `requirements`, `design`, and `tasks` approved.
- [ ] Exact file boundaries defined.
- [ ] Tracking issue created.
- [ ] Base and working branches resolved.
- [ ] Verification commands tested.
- [ ] Political gates confirmed closed.
- [ ] Human owner explicitly authorizes implementation.
