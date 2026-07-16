# C1-FRONT-002 — Premium Slate UI Guidance

Status: Optional implementation companion  
Feature: `C1-FRONT-002 — Campaign Team Command Center`  
Global skill identifier: `premium-slate-ui`

## Intent

When the approved `C1-FRONT-002` design spec authorizes the obsidian-slate visual direction, the implementation agent should check whether the global skill `premium-slate-ui` is available in the agent environment.

Portable discovery hint:

```text
~/.gemini/config/skills/premium-slate-ui/SKILL.md
```

Do not hardcode a user-specific absolute path into application code, documentation, runtime configuration, or tests.

## Activation rule

```text
IF the global skill is available
AND the approved design spec authorizes its visual patterns:
    read the skill instructions
    apply only the relevant design tokens and interaction patterns
    preserve all CampaignOS safety, evidence, and approval requirements
ELSE:
    continue with repository-native, accessible UI patterns
```

The absence of the global skill is not a blocker unless the approved spec explicitly makes a related visual acceptance criterion mandatory.

## Intended visual direction

The skill may support:

- an obsidian-slate Campaign Team Command Center;
- a visually dominant but non-authoritative AI Chief of Staff coordination node;
- a clearly superior human-owner node for the candidate;
- an interactive team canvas;
- department cards with operational state;
- circular transitions between Command Center, Evidence Control Room, agent detail, and future War Room modules;
- premium surfaces, depth, restrained motion, and information hierarchy.

## Non-negotiable hierarchy

The interface must not suggest that AI owns the political mandate.

Required conceptual hierarchy:

```text
Candidate / Human Mandate Owner
              ↓
Human Campaign Governance
              ↓
AI Campaign Chief of Staff
              ↓
Specialized AI Departments and Skills
```

## Canvas requirements

The interactive canvas must have an equivalent semantic list or grid representation.

It must preserve:

- keyboard navigation;
- meaningful headings and landmarks;
- visible focus;
- screen-reader labels;
- touch accessibility;
- narrow-screen fallback;
- status information independent of color;
- direct access to blockers and approval requirements.

The canvas must not be the only way to navigate.

## Circular transition requirements

Circular view transitions are progressive enhancement only.

They must:

- respect `prefers-reduced-motion`;
- preserve focus and browser history;
- degrade to immediate or subtle transitions;
- avoid delaying urgent blockers or approvals;
- avoid hiding evidence classifications;
- remain understandable without motion;
- not become a runtime dependency on the global skill.

## CampaignOS evidence requirements

Premium presentation must retain explicit visual distinctions for:

- official evidence;
- derived values;
- preliminary values;
- hypotheses;
- blockers;
- human approvals;
- closed political gates.

Do not imply certainty through glow, scale, motion, color, or placement when the underlying evidence is preliminary or unresolved.

## Prohibited outcomes

The skill must not introduce or visually encourage:

- targeting;
- voter scoring;
- sensitive-trait profiling;
- mobilization controls;
- automatic political publishing;
- deceptive urgency;
- dark patterns;
- hidden approvals;
- surveillance;
- manipulative personalization;
- AI-as-political-authority framing.

## Verification additions

When `premium-slate-ui` is used, the feature validation plan should add:

- desktop and mobile screenshot review;
- keyboard-only walkthrough;
- reduced-motion verification;
- contrast review;
- zoom and overflow review;
- circular-transition fallback test;
- canvas/list parity check;
- focus restoration after transitions;
- performance review for animation and canvas rendering;
- confirmation that shipped code does not read from the global skill directory.

## Long-session instruction snippet

The approved `C1-FRONT-002` `/goal` may include:

```text
OPTIONAL GLOBAL DESIGN CAPABILITY:
premium-slate-ui

Before frontend implementation, check whether the global skill exists at the portable Gemini skill location. If present and authorized by the approved design spec, read and apply it. Treat it as design-time guidance only. Do not hardcode personal paths, do not make production depend on the global skill, and preserve accessible fallbacks, reduced motion, evidence classifications, human ownership, and closed political gates.
```

## Portability rule

The global skill informs the agent during implementation. The repository must still contain every CSS token, component, asset, interaction implementation, test, and fallback required to build and run the application independently.