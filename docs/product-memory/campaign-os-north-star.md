# CampaignOS Product North Star

Status: Strategic product memory  
Last updated: 2026-07-15  
Decision owner: Human product owner  
Applies to: `Graph-harness-sdlc`, `OS-Electoral`, `LA_muni_RAG`, and the future CampaignOS SaaS
Implementation authority: None by itself

> This document preserves product direction, architectural intent, repository boundaries, safety constraints, and shared vocabulary.
>
> It is not an approved feature specification. No agent may implement product code from this document alone. Every increment must still enter `feature_list.json`, receive an approved spec, obey file boundaries, pass verification, and complete review through `Graph-harness-sdlc`.

---

## 1. Product thesis

CampaignOS is not a political chatbot and not a collection of prompts.

It is an evidence-first Campaign Operating System that gives a candidate or consulting organization:

- a governed virtual campaign team;
- a digital War Room;
- municipal and electoral evidence retrieval;
- procedural guidance;
- human approval gates;
- operational memory;
- auditable decisions;
- reusable campaign workflows;
- a path from candidate workspace to multi-tenant SaaS.

The commercial promise is not “AI that wins elections.”

The product promise is:

> Organize, investigate, decide, approve, execute, and learn through one governed campaign system.

A useful external positioning statement is:

> Your campaign team, digital War Room, and evidence base in one platform.

A more institutional positioning statement is:

> The evidence-first operating system for disciplined, auditable campaign management.

---

## 2. Human authority model

The candidate remains the human mandate owner.

AI is not the candidate, campaign director, legal authority, finance authority, or publication authority.

```text
CANDIDATE / HUMAN MANDATE OWNER
│
├── Personal Executive Assistant
├── Human Campaign Director
├── Human Political Advisor
├── Human Legal Counsel
│
└── AI CAMPAIGN CHIEF OF STAFF
    └── DIGITAL WAR ROOM
```

The candidate should concentrate on:

- values and political purpose;
- citizen listening;
- public representation;
- interviews and debates;
- approval of political positions;
- final decisions requiring human judgment.

The operating system should reduce candidate overload by filtering operational noise, presenting decision-ready briefs, and routing work to the correct department.

The AI Campaign Chief of Staff coordinates. It does not silently decide.

---

## 3. Target operating model

The intended virtual team begins with one orchestrator, a limited set of departmental agents, and reusable skills.

Do not create dozens of independent agents merely to imitate an organization chart.

Recommended initial shape:

```text
1 central orchestrator
8–10 departmental agents
20–30 reusable skills
explicit workflows
human approval gates
```

Definitions:

- **Agent:** owns a mission, context, responsibilities, and stop conditions.
- **Skill:** performs a bounded reusable capability.
- **Workflow:** coordinates several skills and artifacts toward an outcome.
- **Gate:** prevents execution until evidence, permission, or human approval exists.
- **Memory:** preserves reviewed facts, decisions, provenance, and operational state.

---

## 4. Department model

### 4.1 AI Campaign Chief of Staff

Mission:

- operate the War Room;
- maintain current state;
- identify blockers;
- coordinate departments;
- prepare decision briefs;
- route approvals;
- maintain 30/60/90-day plans;
- prevent scope and policy drift.

Example skills:

- Daily War Room Brief;
- Weekly Campaign Brief;
- Decision Gatekeeper;
- Risk Radar;
- Meeting Prep;
- Campaign Health Check;
- Approval Routing;
- Retrospective.

### 4.2 Research and Evidence Director

Mission:

- authenticate sources;
- preserve provenance;
- reconcile conflicting evidence;
- maintain electoral and municipal baselines;
- expose unknowns and research gaps;
- prevent unsupported claims.

Example skills:

- Official Source Finder;
- Evidence Validator;
- Electoral Baseline;
- Source Reconciliation;
- Research Gap Detector;
- Evidence Register Update;
- Citation Pack Builder.

`OS-Electoral` currently provides the strongest foundation for this department.

### 4.3 Strategy and War Room Director

Mission:

- convert signals and evidence into scenarios;
- distinguish strategic decisions from tactics;
- maintain objectives, constraints, assumptions, and decision logs;
- coordinate War Room cadence.

This department must not confuse activity volume with strategy.

### 4.4 Candidate Brand and Reputation Director

Mission:

- document candidate identity, purpose, biography, values, attributes, proof points, reputation, and perception gaps;
- evaluate congruence between what the candidate is, says, does, and projects;
- support media readiness without manufacturing a false persona.

Example skills:

- Candidate Identity Interview;
- Biography Builder;
- Values Map;
- Attribute Evidence Map;
- Reputation Baseline;
- Perception Gap Analysis;
- Behavioral Consistency Review;
- Media Presence Review;
- Brand Evolution Log.

Brand work must follow research. Communication must not begin before identity, evidence, objectives, audience context, and approvals are clear.

### 4.5 Policy and Municipal Government Director

Mission:

- convert documented problems into feasible municipal proposals;
- distinguish municipal competence from national responsibility;
- document legal, budgetary, operational, and institutional dependencies;
- maintain a promise and feasibility register.

Example skills:

- Problem Tree;
- Municipal Competency Check;
- Proposal Builder;
- Feasibility Review;
- Cost Assumption Review;
- Promise Tracker;
- First 100 Days Draft.

### 4.6 Communications and Media Director

Mission:

- work only from approved strategy, brand, claims, and evidence;
- prepare speeches, interviews, press briefs, debate materials, and content drafts;
- validate message consistency and factual support.

Sensitive actions such as publishing, sending messages, activating paid media, or issuing a public position require human approval.

### 4.7 Legal and Electoral Compliance Officer

Mission:

- maintain legal calendars;
- identify approval and reporting obligations;
- review propaganda, contracts, finance, permissions, and electoral constraints;
- escalate legal ambiguity to qualified human counsel.

The agent may prepare structured analysis. It must not present itself as final legal authority.

### 4.8 Finance and Administration Director

Mission:

- budget, cash flow, commitments, vendors, invoices, expense approval, contribution records, limits, and reconciliation;
- preserve auditability and approval history.

### 4.9 Operations and Team Director

Mission:

- team structure;
- responsibilities;
- onboarding;
- calendars;
- meetings;
- tasks;
- training;
- events;
- logistics;
- workload and follow-up.

Field mobilization remains a gated capability. The system must not infer individual political preference or build voter-level persuasion scores.

### 4.10 Security and Information Protection Officer

Mission:

- security onboarding;
- access review;
- phishing and attachment risk education;
- credential hygiene;
- incident intake;
- data classification;
- vendor security checks;
- sensitive-document handling.

No offensive cyber capability, surveillance, credential theft, or covert collection belongs in the product.

### 4.11 Performance and Learning Analyst

Mission:

- measure process performance;
- evidence coverage;
- task completion;
- decision follow-through;
- bottlenecks;
- experiment review;
- retrospectives;
- lessons learned.

It must not generate individual voter support, susceptibility, or persuasion scores.

---

## 5. War Room workflow

The Digital War Room is a structured decision process, not a generic chat room.

```text
Signals
  ↓
Evidence validation
  ↓
Situation assessment
  ↓
Decision options
  ↓
Legal / financial / evidence checks
  ↓
Human approval
  ↓
Task assignment
  ↓
Execution tracking
  ↓
Learning
```

Every important decision should preserve:

- question or problem;
- evidence used;
- source authority;
- assumptions;
- options considered;
- risks;
- decision owner;
- approval status;
- resulting tasks;
- later outcome.

---

## 6. Three product planes

### 6.1 Governance Plane

Owns:

- organizations and campaigns;
- users, roles, and permissions;
- agent autonomy levels;
- human approval gates;
- logs and decision records;
- evidence classification;
- policy enforcement;
- audit trail;
- tenant isolation;
- safety constraints.

This plane is the primary differentiator between a production system and a prompt collection.

### 6.2 Intelligence Plane

Owns:

- document registry;
- ingestion;
- versions;
- chunks and citable sections;
- retrieval;
- RAG;
- evidence graph;
- municipal and electoral knowledge;
- campaign memory;
- structured source taxonomies;
- confidence and gaps.

`LA_muni_RAG` is the current foundation of this plane.

### 6.3 Execution Plane

Owns:

- briefs;
- workflows;
- task creation;
- document drafts;
- meeting preparation;
- approvals;
- procedural checklists;
- controlled integrations;
- execution history.

Sensitive outbound actions remain human-gated.

---

## 7. Repository responsibilities

### 7.1 `Graph-harness-sdlc`

Role: delivery-control system.

Owns:

- spec-driven delivery;
- feature lifecycle;
- role separation;
- file boundaries;
- execution modes;
- verification gates;
- review and production-readiness artifacts;
- reusable software-delivery skills and templates;
- decision records for how product changes are built.

It does not own campaign evidence or the production RAG corpus.

### 7.2 `OS-Electoral`

Role: campaign evidence and governance kernel, currently Antigua-first.

Owns:

- campaign charter and current state;
- evidence register;
- electoral and territorial baselines;
- source reconciliation;
- decision logs;
- political gates;
- campaign-specific research artifacts;
- Evidence Control Room and future Campaign Team Command Center;
- the campaign-domain contracts that define safe use of evidence.

It should consume RAG capabilities rather than reimplement a second retrieval engine.

### 7.3 `LA_muni_RAG`

Role: reusable evidence-first RAG and procedural workflow engine.

Current capabilities include:

- PostgreSQL document registry and versions;
- citable sections;
- keyword, phrase, and hybrid retrieval;
- evidence response contracts;
- deterministic answer layers;
- chat and agent APIs;
- procedural workflow composition;
- confidence, citations, gaps, and validation warnings;
- domain-pack registry and validation;
- feedback infrastructure;
- source-link safety;
- municipal Antigua default pack.

The future campaign integration should be implemented as a validated domain pack or a deliberately separated campaign-specific pack, not as ad hoc prompts.

Candidate domain-pack direction:

```text
campaign-antigua
├── branding and Spanish UI labels
├── evidence authority taxonomy
├── electoral research workflows
├── municipal policy workflows
├── candidate-brand workflows
├── War Room workflows
├── legal/compliance workflow boundaries
├── validation rules
├── seed questions
└── evaluation cases
```

The municipal pack should remain authoritative for municipal procedures. The campaign pack may reference it, but must not silently reinterpret municipal procedure as campaign strategy.

### 7.4 Future SaaS repository or product shell

Role: multi-tenant product application.

It may eventually own:

- organization and campaign tenancy;
- authentication and billing;
- candidate and agency workspaces;
- Campaign Team Command Center;
- approval inbox;
- War Room UI;
- agent runtime orchestration;
- integrations;
- white-label configuration;
- product analytics;
- deployment and operations.

Do not create this repository or split services until an approved architecture spec justifies the boundary.

---

## 8. Integration model

The intended relationship is:

```text
Graph-harness-sdlc
  controls how changes are specified, built, verified, reviewed, and shipped

OS-Electoral
  defines campaign evidence, governance, state, gates, and domain artifacts

LA_muni_RAG
  retrieves evidence and composes evidence-backed municipal/procedural workflows

CampaignOS SaaS
  presents the virtual team, War Room, approvals, workspaces, and multi-tenant product
```

A future request path may look like:

```text
Candidate question
  ↓
Campaign Chief of Staff
  ↓
Intent and gate classification
  ↓
OS-Electoral campaign state and permissions
  ↓
LA_muni_RAG campaign/municipal domain pack retrieval
  ↓
Evidence response with citations, confidence, and gaps
  ↓
Workflow or decision brief
  ↓
Human approval where required
  ↓
Execution record and learning
```

---

## 9. Evidence contract

Every important claim should be able to answer:

- Where did it come from?
- What authority class does the source have?
- Is it official, preliminary, derived, campaign research, perception, hypothesis, or unknown?
- What date and territorial scope apply?
- Who reviewed it?
- What limitations remain?
- In which decision was it used?

Recommended evidence classes:

- `OFFICIAL_FINAL`;
- `OFFICIAL_PRELIMINARY`;
- `OFFICIAL_REFERENCE`;
- `CAMPAIGN_RESEARCH`;
- `DERIVED_CALCULATION`;
- `PERCEPTION_RESEARCH`;
- `HYPOTHESIS`;
- `UNKNOWN`.

Extraction success must never automatically promote evidence to decision evidence.

```text
Raw extraction
  ↓ human or deterministic validation
Curated evidence
  ↓ explicit decision approval
Decision evidence
```

---

## 10. Product surfaces

### Candidate Workspace

For one candidate and their team:

- daily brief;
- decision inbox;
- meetings;
- evidence;
- proposals;
- legal calendar;
- budget status;
- candidate brand;
- campaign team;
- blockers and approvals.

### Campaign Team Command Center

The target homepage should visually represent the campaign team.

```text
CANDIDATE / HUMAN OWNER
        ↓
AI CAMPAIGN CHIEF OF STAFF
        ↓
Research | Strategy | Brand | Policy | Legal | Finance | Comms | Operations | Security | Learning
```

Each agent card should show:

- department;
- mission;
- state;
- available skills;
- required inputs;
- blocker;
- autonomy level;
- approval owner;
- last execution;
- pending artifacts.

Suggested states:

- `ACTIVE`;
- `RESEARCH_ONLY`;
- `SETUP_REQUIRED`;
- `LOCKED`;
- `BLOCKED`;
- `REVIEW_REQUIRED`.

### Evidence Control Room

Existing first module:

- evidence metrics;
- source classifications;
- reconciliation;
- blockers;
- political gates;
- safety contract.

It becomes a module inside the broader Command Center, not the entire product homepage.

### Daily War Room

Future surface:

- signals;
- brief;
- risks;
- decisions;
- approvals;
- assigned actions;
- minutes;
- outcome follow-up.

### Candidate Brand and Reputation Workspace

Future surface:

- identity;
- biography;
- purpose;
- values;
- attributes;
- proof points;
- perception research;
- behavior consistency;
- reputation timeline;
- visual identity;
- speaking style;
- media readiness;
- approval history.

### Agency Workspace

Future commercial tier:

- multiple campaigns;
- client isolation;
- templates and playbooks;
- reusable domain packs;
- consultant permissions;
- white label;
- portfolio reporting;
- campaign cloning with explicit data isolation.

---

## 11. Commercial direction

Potential editions:

### Candidate Edition

For candidates and small teams.

### Campaign Team Edition

For departmental campaign organizations.

### Consultant / Agency Edition

For firms managing multiple campaigns.

### Government Transition Edition

For transition, first 100 days, commitments, cabinet workflows, and policy delivery after an election.

Possible long-term marketplace:

- country-specific compliance packs;
- municipal policy packs;
- media training workflows;
- debate preparation;
- crisis-management playbooks;
- finance and audit packs;
- consultant-authored skills subject to review and safety gates.

---

## 12. Safety and ethical boundaries

CampaignOS must not provide or operationalize:

- disinformation;
- fabricated evidence;
- deceptive impersonation;
- personal attacks based on rumor;
- exploitation of individual psychological vulnerabilities;
- individual persuadability scores;
- sensitive-trait political profiling;
- unlawful microtargeting;
- covert surveillance of citizens;
- voter-level preference inference;
- automatic political publication without approval;
- offensive cybersecurity;
- unauthorized credential or data collection.

Allowed direction:

- citizen listening in aggregate;
- public-issue analysis;
- evidence-based proposals;
- lawful and factual contrast;
- transparent communication;
- institutional process support;
- human-reviewed political decisions;
- privacy-preserving analytics;
- public and authorized source retrieval.

---

## 13. Moat

The defensible advantage is not the underlying model provider.

The moat is the combined system:

```text
Political operating model
+ evidence graph
+ municipal and electoral domain packs
+ campaign memory
+ workflows
+ approval gates
+ auditability
+ candidate-brand methodology
+ country-specific compliance
+ reusable consultant playbooks
+ safe multi-tenant operations
```

A competitor can copy a card called “Speech Writer.”

It is harder to copy a governed evidence lifecycle, decision history, validated domain packs, approval system, and accumulated campaign-operating memory.

---

## 14. Roadmap direction

This is directional memory, not approved scope.

### Phase 1 — Evidence and Governance Kernel

- evidence register;
- official-source reconciliation;
- territorial and electoral baselines;
- gates;
- blockers;
- decision logs;
- Evidence Control Room.

Status: substantially underway in `OS-Electoral`.

### Phase 2 — Campaign Team Command Center

- candidate as human owner;
- AI Chief of Staff;
- department cards;
- skill inventories;
- blockers;
- approval requirements;
- agent detail view.

### Phase 3 — Daily War Room

- signals;
- brief;
- decisions;
- assignments;
- minutes;
- follow-up;
- learning.

### Phase 4 — Candidate Brand and Reputation

- identity interview;
- biography;
- values;
- attributes;
- proof points;
- perception gaps;
- media readiness.

### Phase 5 — Approval Inbox and Decision Ledger

- pending approvals;
- evidence packs;
- decision owners;
- audit trail;
- expiry and revision handling.

### Phase 6 — RAG and Agent Runtime Integration

- campaign domain pack;
- municipal-domain interoperability;
- retrieval contracts;
- workflow execution;
- evaluations;
- memory boundaries.

### Phase 7 — Multi-tenant SaaS

- organizations;
- campaigns;
- authentication;
- billing;
- permissions;
- data isolation;
- operations;
- white label.

### Phase 8 — Marketplace and Transition Product

- reviewed expert packs;
- country packs;
- agency distribution;
- government-transition extension.

---

## 15. Harness execution rule

This memory may inspire features, but never bypass the harness.

For every implementation increment:

1. create or update the feature in `feature_list.json`;
2. create `requirements.md`, `design.md`, and `tasks.md`;
3. define MVP or SHIP mode;
4. define files agents may read, touch, and must not touch;
5. obtain human approval;
6. implement only the approved scope;
7. run specified verification;
8. complete independent review;
9. complete production review for SHIP mode;
10. update progress and decision records.

The product north star is stable memory.

The spec is executable authority.

---

## 16. Current near-term product question

The next product decision is not whether to build “all agents.”

It is whether the Evidence Control Room should evolve into a Campaign Team Command Center while preserving:

- candidate human ownership;
- read-only evidence mode;
- visible gates;
- department status;
- approval requirements;
- no real agent execution until a runtime spec is approved.

A likely future feature candidate is:

```text
C1-FRONT-002 — Campaign Team Command Center
```

Expected bounded scope:

- visual organization chart;
- candidate/human-owner node;
- AI Chief of Staff node;
- department cards;
- states and blockers;
- skill list;
- agent detail drawer;
- Evidence Control Room as an internal module;
- responsive and accessible UI;
- no outbound execution;
- no targeting;
- no mobilization;
- no multi-tenant backend yet.

This candidate feature must still be formally specified and approved before implementation.
