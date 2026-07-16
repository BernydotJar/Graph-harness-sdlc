# Premium Slate UI — Global Design Capability

Status: Optional global agent capability  
Skill identifier: `premium-slate-ui`  
Applies to: future frontend specs and approved long-session implementation goals  
Implementation authority: None by itself

## Purpose

`premium-slate-ui` is a reusable global agent skill that provides a premium obsidian-slate visual system for product interfaces.

Its intended capabilities include:

- obsidian and slate visual hierarchy;
- premium dark-surface composition;
- interactive canvas patterns;
- circular view transitions;
- spatial navigation between product modules;
- polished dashboard and command-center presentation.

The skill is installed in the user's global Gemini configuration and may be available to future AI sessions, including long-running `/goal` sessions.

A typical portable discovery location is:

```text
~/.gemini/config/skills/premium-slate-ui/SKILL.md
```

The repository must not hardcode a user-specific absolute path such as `/Users/<name>/...`.

## Capability, not dependency

This skill is not owned by `harness-sdlc`, `OS-Electoral`, or `LA_muni_RAG`.

It must be treated as an optional environment capability:

```text
if premium-slate-ui is available and the approved spec authorizes it:
    read the skill instructions
    apply the relevant design system
    validate accessibility and performance
else:
    continue with repository-native design tokens and standard accessible UI
```

The absence of the global skill must not block an otherwise executable feature unless the approved spec explicitly makes its visual output a required acceptance criterion.

Agents must not copy the global `SKILL.md` into a product repository unless a human explicitly authorizes vendoring or adaptation.

## Harness rule

The skill may influence implementation only after:

1. the feature is registered;
2. requirements, design, and tasks are approved;
3. file boundaries authorize frontend changes;
4. the spec identifies the intended visual behavior;
5. the long-session prompt lists `premium-slate-ui` as an optional or required capability;
6. verification includes accessibility, motion, responsiveness, and performance checks.

Product memory does not activate the skill by itself.

## CampaignOS design direction

For CampaignOS, the skill can support:

- the Campaign Team Command Center;
- the AI Campaign Chief of Staff focal node;
- department cards and status surfaces;
- Evidence Control Room navigation;
- agent detail drawers;
- the Daily War Room canvas;
- module-to-module spatial transitions;
- clear separation of `ACTIVE`, `RESEARCH_ONLY`, `SETUP_REQUIRED`, `LOCKED`, and `BLOCKED` states.

The candidate must remain the visible human mandate owner. Visual hierarchy must not imply that AI is the political authority or final decision owner.

## Circular transition policy

Circular view transitions are enhancement-only.

They must:

- preserve browser navigation and focus;
- degrade gracefully when unsupported;
- respect `prefers-reduced-motion`;
- avoid obscuring evidence classification or approval state;
- avoid delaying urgent information;
- never become required to understand the interface;
- remain testable on keyboard and touch devices.

When reduced motion is requested, use an immediate or subtle opacity transition instead.

## Interactive canvas policy

An interactive canvas may organize agents, modules, workflows, or evidence relationships, but it must not become the sole navigation mechanism.

A conforming implementation must provide:

- semantic headings and landmarks;
- keyboard-reachable alternatives;
- readable list or grid fallback;
- visible focus states;
- sufficient contrast;
- meaningful labels independent of color;
- responsive behavior on narrow screens;
- no hidden political actions behind decorative interactions.

## Evidence and political-safety constraints

Premium presentation must never blur evidence boundaries.

The UI must continue to distinguish:

- official evidence;
- derived values;
- preliminary values;
- hypotheses;
- blockers;
- human approvals;
- closed political gates.

The skill must not introduce:

- targeting;
- voter scoring;
- sensitive-trait profiling;
- automatic publication;
- mobilization controls;
- manipulative dark patterns;
- deceptive urgency;
- hidden consent;
- misleading visual certainty.

## Verification expectations

A feature using `premium-slate-ui` should verify, at minimum:

- desktop and mobile layouts;
- keyboard navigation;
- focus visibility;
- color contrast;
- reduced-motion behavior;
- overflow and zoom;
- circular transition fallback;
- canvas/list parity;
- no external tracking scripts;
- no personal absolute paths;
- no dependency on the skill at runtime unless explicitly packaged and approved;
- no change to political gates.

## Portability note

The design capability belongs to the agent environment, not the shipped application.

The application must contain all CSS, assets, components, and tests needed to run independently after implementation. A production build must not read from `~/.gemini/config/skills/` or any other developer-specific configuration directory.

## First intended use

The first proposed use is:

```text
C1-FRONT-002 — Campaign Team Command Center
```

That feature may use `premium-slate-ui` to create the obsidian-slate command-center experience, interactive team canvas, and circular module transitions, provided the approved design spec explicitly authorizes those behaviors and preserves the fallbacks and safety rules above.
