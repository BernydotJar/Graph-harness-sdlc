# Graph Harness SDLC

**Autonomia strutturata su un grafo eseguibile, con stato tipizzato, evidenza tracciabile e riparazione localizzata.**

> [English canonical README](../../README.md) · [Español](README.es.md) · [Português](README.pt.md)

> La documentazione inglese è la versione canonica. Questa traduzione può essere leggermente indietro rispetto alla versione principale.

`Graph Harness SDLC` è un runtime di esecuzione riutilizzabile e una metodologia di engineering per costruire software con agenti AI senza dipendere da una conversazione monolitica o da loop che perdono contesto.

Trasforma requisiti, task, decisioni, risultati di verifica e failure in nodi e relazioni esplicite che possono essere eseguiti, auditati, ripresi e riparati.

**L'obiettivo non è generare attività. L'obiettivo è completare il prodotto.**

## Modello centrale

```text
Requirement
  -> Specification
  -> Human approval
  -> Task graph
  -> Executor
  -> Verification
  -> Evidence
  -> Gate
  -> Done / Localized repair
```

L'agente non è il centro dell'architettura. È un executor intercambiabile che opera all'interno di un grafo governato da dipendenze, capability, permessi e gate.

## Cosa fornisce

- Spec-Driven Development
- Harness Engineering
- Loop Engineering
- grafi di esecuzione tipizzati
- stato di esecuzione tipizzato
- scheduling dependency-aware
- separazione di ruoli e capability
- gate di approvazione umana
- limiti di file e permessi
- evidenza verificabile
- quality gate deterministici
- checkpoint persistenti e recovery
- riparazione localizzata del sottografo interessato
- decisioni e debito tecnico tracciabili
- esecuzione riprendibile di sessioni lunghe
- stati terminali espliciti

## Ciclo di esecuzione

```text
Nodo READY
    -> Producer
    -> Critic / Red Team
    -> Fixer
    -> Independent Verifier
    -> Release Gate
    -> Evidenza persistente
    -> Nodo READY successivo
```

Una feature non è completa semplicemente perché esiste il codice. È completa quando la sua evidenza soddisfa tutti i gate richiesti e il grafo rimane in uno stato valido.

## Stati terminali

- `COMPLETED` — non rimane lavoro di engineering utile, sicuro, sbloccato e verificabile.
- `PARTIAL_WITH_DOCUMENTED_BLOCKERS` — tutto il lavoro rimanente dipende esclusivamente da blocker esterni documentati, approvazione umana, infrastruttura o credenziali non disponibili oppure decisioni esplicite di prodotto.
- `SAFETY_STOP` — continuare violerebbe vincoli di sicurezza, integrità o gate umani.

## Principio guida

```text
Prompt -> Runtime -> Execution graph -> Executors -> Evidence -> Gates -> Persistent state
```

Cloud Sandbox controlla **dove** un agente può operare.

Graph Harness SDLC controlla **come** il lavoro di engineering procede e viene verificato.

Il prodotto definisce **quale** capacità di business stiamo costruendo.
