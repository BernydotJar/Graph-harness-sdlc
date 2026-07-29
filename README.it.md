<div align="center">

<img src="assets/graph-harness-cats.svg" alt="Tre gatti collegati come grafo eseguibile di delivery del software" width="900" />

# Graph Harness SDLC

**Autonomia strutturata su un grafo eseguibile di delivery del software.**

[English — canonico](README.md) · [Español](README.es.md) · [Português](README.pt.md) · [Italiano](README.it.md)

</div>

Graph Harness SDLC è un runtime di esecuzione e una metodologia di ingegneria per programmi autonomi e di lunga durata dedicati allo sviluppo software.

Trasforma la delivery da una sequenza di prompt isolati in un grafo eseguibile persistente composto da stato tipizzato, dipendenze esplicite, quality gate, evidenze tracciabili e riparazione localizzata.

**L'inglese è la lingua canonica della documentazione.** Questa traduzione migliora l'accessibilità, mentre identificatori normativi, schemi e contratti del runtime rimangono in inglese.

## Principio fondamentale

> Il grafo di esecuzione è la fonte di verità. Gli agenti sono esecutori intercambiabili.

Una feature non è completa solo perché esiste del codice. È completa soltanto quando le sue evidenze soddisfano tutti i gate richiesti e il grafo rimane in uno stato valido.

## Cosa fornisce

- Grafi di sviluppo eseguibili
- Stato di esecuzione tipizzato
- Scheduling consapevole delle dipendenze
- Checkpoint persistenti
- Separazione tra producer, critic, fixer e verifier
- Quality gate deterministici
- Completamento basato su evidenze
- Riparazione localizzata
- Gate di approvazione umana
- Esecuzione riprendibile per sessioni lunghe
- Stati terminali espliciti

## Ciclo di esecuzione

```text
Nodo pronto
    ↓
Producer
    ↓
Critic / Red Team
    ↓
Fixer
    ↓
Verifier indipendente
    ↓
Release Gate
    ↓
Evidenza persistente
    ↓
Nodo pronto successivo
```

## Obiettivo

L'obiettivo non è generare attività.

**L'obiettivo è completare il prodotto.**

L'esecuzione continua finché il repository raggiunge uno dei tre stati terminali del programma:

- `COMPLETED`
- `PARTIAL_WITH_DOCUMENTED_BLOCKERS`
- `SAFETY_STOP`

Questi risultati riguardano l'intero programma e sono distinti dagli stati dei nodi come `done`, `blocked` e `repair_required`. Vedere [Terminal states](docs/terminal-states.md).

## Modello del runtime

Un repository consumer fornisce un grafo `graph-harness.project.v1`, un ledger append-only `graph-harness.event.v1` e adapter di dominio fissati a una revisione specifica del framework. Il runtime deriva `graph-harness.state.v1` e governa transizioni, dipendenze, evidenze, gate, checkpoint e riparazione localizzata.

Il runtime non concede autorità per merge, release, deployment, spese, modifica dei segreti o effetti esterni. Queste decisioni restano sotto gate umani o del repository consumer.

## Avvio rapido

```sh
./init.sh
```

## Documentazione

- [Indice della documentazione](docs/README.md)
- [Concetti](docs/concepts.md)
- [Architettura del runtime](docs/runtime-architecture.md)
- [Architettura del sistema](docs/system-architecture.md)
- [Tutorial](docs/tutorials.md)
- [Esempi](examples/)
- [Riferimento](docs/reference.md)

Graph Harness SDLC non è un'applicazione né una raccolta di prompt. È il sistema operativo riutilizzabile di esecuzione che i repository consumer usano per consegnare software attraverso un grafo governato.
