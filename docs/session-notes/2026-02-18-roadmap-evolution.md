# Roadmap Evolution Session — 2026-02-18

> **Participants:** Mustafa Uzumeri, Antigravity Agent  
> **Repository:** CosolventAI  
> **File modified:** `ROADMAP.md`  
> **Duration:** ~1 hour  
> **Date:** February 18, 2026

---

## Overview

This session evolved the CosolventAI roadmap through six major architectural decisions, each building on the last. The session began with expanding the marketplace model beyond buyers and sellers, and ended with a fundamentally reshaped vision: Cosolvent as a **configurable framework for thin market matchmaking** that produces **domain-specific Handoff Artifacts** — not a single-instance agricultural e-commerce platform.

The roadmap grew from ~920 lines to ~1,110 lines. All changes were made to `ROADMAP.md`.

---

## Decision 1: Multilateral Marketplace

### The question
The marketplace was modeled as bilateral (buyers and sellers). Real thin markets — especially cross-border trade — require more parties.

### The decision
Expand from two to **three participant categories**:

| Category                         | Role                            | Matching pattern                   |
| -------------------------------- | ------------------------------- | ---------------------------------- |
| Principals (Sellers)             | Offer goods/services            | Matched against buyer requirements |
| Principals (Buyers)              | Seek goods/services             | Matched against seller offerings   |
| Facilitators (Service Providers) | Enable deals between principals | Matched against deal requirements  |

Facilitators include customs brokers, shipping/logistics, quality inspectors, trade finance providers, insurance underwriters, legal/compliance advisors, and translation/cultural mediators.

### Why it matters
Facilitators don't discover the marketplace through gallery browsing — they're pulled in by deal requirements. This is a fundamentally different matching pattern ("deal-attached matching") from participant-to-participant matching.

### What changed in the roadmap
- **Section 3** renamed "Multilateral Marketplace — Beyond Buyers and Sellers" and expanded with facilitator types table, three participant categories table, and four new subsections (3.1–3.4)
- **Section 4** (Three-Layer Architecture) updated to show how gallery and matching profiles apply to facilitators
- **Section 5** (Matching Engine) updated to describe three search modes (gallery, participant-to-participant, deal-to-facilitator)
- **Section 22** (Data Model) added facilitator profiles, deals, deal role slots, deal participants
- **Section 23** (Frontend) added facilitator dashboard and deal assembly view
- **Phase 1** items updated to include facilitator registration and type-aware embedding templates
- **Phase 3** expanded with deal entity, facilitator search, deal assembly UI, facilitator dashboard
- **Cross-cutting principle #10** added: "Deals need more than two parties"

---

## Decision 2: Deal Entity and Role Slots

### The question
How does the system manage multi-party deal assembly?

### The decision
Introduce a **Deal data model** with:
- Principals involved (buyer, seller)
- Product/service, route, volume, value, timeline
- Quality/certification requirements
- **Role slots** — a list of facilitator roles the deal needs, each with a lifecycle status:
  - `needed` → `searching` → `proposed` → `confirmed` → `not-needed`

When a buyer-seller match progresses to deal structuring, the system analyzes deal requirements, determines needed facilitator roles, searches for matching facilitators, and proposes them to the principals.

### Why it matters
The role slot model means the system can systematically identify what a deal needs and find the right service providers — rather than leaving principals to figure it out on their own.

---

## Decision 3: Two-Track Implementation Phasing

### The question
Phases 4 (Pricing, Aggregation, Intelligence) and 5 (Accessibility, Multimodal, Framework) were sequenced 4→5, but Phase 5 had almost no dependencies on Phase 4.

### The decision
Restructure from 6 sequential phases to a **shared foundation + two parallel tracks**:

```
                    ┌─── Track A: Marketplace Depth ──────────────────────┐
                    │   Deals, agents, pricing, intelligence              │
Phase 1 → Phase 2 ─┤                                                     │
                    │                                                     │
                    └─── Track B: Platform Breadth ───────────────────────┘
                        Accessibility, framework, simulation, global reach
```

- **Shared Foundation:** Phase 1 (Three-Layer Foundation & Multilateral Matching), Phase 2 (Trust, Transparency & Admin Control)
- **Track A:** A1 (Deals, Facilitators & Memory), A2 (Pricing, Aggregation & Market Intelligence)
- **Track B:** B1 (Accessibility, Multimodal Input & Framework), B2 (ClientSynth, Digital Twins & Global Scale)

### Why it matters
These tracks represent **structurally independent concerns**:
- Track A deepens the marketplace (better at closing deals) — driven by transaction sophistication
- Track B widens the platform (accessible to more markets) — driven by reach and adaptability

New depth features (smarter agents, richer deal types) don't block new breadth features (new input channels, new verticals), and vice versa. Only one cross-track dependency exists: B1.6 (WhatsApp/SMS) needs A1.12 (notification service), but A1.12 has no dependencies and can be pulled forward.

---

## Decision 4: Communication Architecture (Section 3.5)

### The question
How do participants communicate safely as they move from discovery to deal-making?

### The decision
Communication is **privacy-layered and context-scoped** — you don't "message a user," you communicate within a shared context (match or deal) that both parties opted into.

Five stages:

| Stage                | Channel                        | Privacy model                                             |
| -------------------- | ------------------------------ | --------------------------------------------------------- |
| Gallery browsing     | No direct contact              | Public profile only                                       |
| Match introduction   | System-mediated intro          | Match rationale + gallery profiles; no private data       |
| Match conversation   | Scoped messaging               | Between two parties + AI; only what each chooses to share |
| Deal channel         | Multi-party deal space         | All deal participants communicate within deal scope       |
| Selective disclosure | Document elevation within deal | Per-item, per-counterparty, revocable                     |

Four design principles:
1. **Context-scoped** — prevents spam, provides shared framing
2. **AI introduces, then steps back** — matching algorithm creates introductions, not users
3. **Trust unlocks channels** — can't skip stages
4. **Platform holds the record** — for disputes, AI learning, compliance

### Why it matters
The three-layer information model isn't just a data storage concept — it's a **communication governance model**. Each layer defines what can flow to whom, through what channel, under what conditions. Communication channels are how trust gradation actually materializes for users.

---

## Decision 5: Platform Scope — From Matching to Handoff (Section 3.6)

### The question
Should the V1 platform handle the full transaction lifecycle through to settlement?

### The decision
**No.** V1 ends at **handoff**, not settlement.

The analogy is a dating site: match → introduce → build confidence → schedule the meeting → done. What happens at the meeting is between the parties.

The platform lifecycle in V1:
```
Gallery Browsing → AI Match → Introduction → Conversation → Deal Assembly → Handoff Artifact → Offline
```

**The Handoff Artifact is the platform's primary deliverable** — a structured package designed to be given to downstream professionals (bank, lawyer, shipper) who will structure and execute the transaction. It's assembled from information already in the system: gallery profiles, matching signals (sanitized), conversation context, shared documents, facilitator recommendations, and regulatory flags.

### The generalization insight
The Handoff Artifact is a **framework concept, not a trade-specific document**. Every thin market deployment produces a domain-specific version:

| Vertical                | Handoff Artifact        |
| ----------------------- | ----------------------- |
| Cross-border trade      | **Deal Brief**          |
| Remote mental health    | **Plan of Care**        |
| Specialty manufacturing | **Production Brief**    |
| Art / collectibles      | **Transaction Package** |
| Niche real estate       | **Deal Package**        |

The template is admin-configurable per deployment — connected to the Slots Architecture and `MarketDefinition` schema. Each vertical defines the artifact's name, sections, field mappings, downstream consumer roles, and compliance flags.

### What changed in the roadmap
- **Section 3.6** added with full platform scope definition, lifecycle diagram, vertical examples table, and configurability requirements
- **A1.10** (deal progression) reframed to end at Handoff Artifact generation, not settlement
- **A1.11** added: Handoff Artifact generator (admin-configurable template)
- **A2** description updated to note these items extend beyond the core handoff model
- **B2.6** (fulfillment/settlement) marked as future expansion — vertical-specific, not V1
- **Cross-cutting principles #11, #12, #13** added

### Why it matters
This clarifies what "done" means for V1 — a question that, left unanswered, leads to scope creep. It also establishes that the platform's value proposition is **finding and qualifying counterparties**, not executing transactions. In thin markets, finding each other is the hard part; closing the deal can use existing mechanisms.

---

## Decision 6: Multi-Model LLM Routing

### The question
The admin UI shows a single primary LLM and a single embedding model. Is that sufficient?

### The decision
**No.** Real-world deployments will need **multiple LLMs simultaneously**, each assigned to specific tasks.

Example: A marketplace serving Ethiopian participants may receive documents in Amharic. General-purpose LLMs handle Amharic poorly, but specialized HuggingFace models do well. The system needs to route Amharic translation tasks to the specialist model while using GPT-5 for general reasoning and a separate model for embeddings — all at the same time.

### Current state (good foundation, key gaps)
The `config.json` already has the right skeleton — named services (`translate`, `metadata_extraction`, `profile_generation`) each pointing to a specific provider. But:
- **Single client type** — `ClientName` enum only has `OPENROUTER`
- **No task-level routing** — can't route within a service based on language or document type
- **No prompt-to-model binding** — prompts don't declare which model they're tuned for
- **No fallback chains** — if a specialist model is down, no automatic fallback

### What changed in the roadmap
- **Section 21** (Slots Architecture) — Intelligence Slot description expanded to explain multi-model routing with the Amharic example. Four new gaps documented. Five new required changes: multiple client types, task-level routing, prompt-to-model binding, fallback chains, admin UI for model management.
- **Phase 2** — Item 2.1 expanded to include multi-provider registration and task-level routing. Item 2.2 expanded to include prompt-to-model binding and fallback chains. New item 2.3 added: extend `ClientName` and `LLMClient` for multiple provider types. Subsequent items renumbered 2.4–2.9.

---

## Cross-Cutting Principles — Grouped for Presentation

The 13 cross-cutting principles were reordered from their original ad-hoc sequence into four presentation-ready groups that build a narrative arc:

### A — Why thin markets are different
1. **Structural desire must exist.** AI can't create demand that doesn't exist.
2. **Test with thin-market dynamics.** Few participants, infrequent transactions, high stakes.
3. **Trust is the prerequisite, not a feature.** Does this increase willingness to engage?

### B — What the platform does
4. **The framework defines the structure; the vertical defines the content.** Admin-configurable per deployment.
5. **Deals need more than two parties.** Match deals to service providers, not just buyers to sellers.
6. **The platform's job is to get parties to the table, not to run the table.** Handoff, not settlement.

### C — How information flows
7. **Privacy is a prerequisite.** Fewer participants = more identifiable data.
8. **Gallery is for discovery, matching is for depth.** Never conflate the two.
9. **Users own their information boundaries.** Per-document, editable, visible.
10. **Communication is scoped, not open.** Within match/deal contexts, not general messaging.
11. **Never destroy information through premature standardisation.** Let AI handle heterogeneity.

### D — How we implement it
12. **Design for cognitive bandwidth constraints.** Curated subsets, not data dumps.
13. **Prompt-driven, not code-driven.** Business logic in prompts, not hardcoded.

The narrative arc: *Why this matters → What we build → How it works → How we execute.*

---

## Summary of All Roadmap Sections Modified

| Section         | Change type          | Description                                                             |
| --------------- | -------------------- | ----------------------------------------------------------------------- |
| 3 (Marketplace) | Major expansion      | Bilateral → multilateral; added 3.1–3.6                                 |
| 3.5             | New subsection       | Communication architecture                                              |
| 3.6             | New subsection       | Platform scope, Handoff Artifact, vertical examples                     |
| 4 (Three-Layer) | Minor update         | Gallery/matching profiles apply to facilitators                         |
| 5 (Matching)    | Minor update         | Three search modes                                                      |
| 21 (Slots)      | Major expansion      | Multi-model routing, four new gaps, five new changes                    |
| 22 (Data Model) | Minor update         | Facilitator profiles, deals, role slots, deal participants              |
| 23 (Frontend)   | Minor update         | Facilitator dashboard, deal assembly view                               |
| 26 (Phases)     | Major restructure    | Two-track phasing; Phase 2 expanded; A1.10-A1.12 updated; B2.6 reframed |
| Principles      | Reordered & expanded | Grouped A–D; added #11, #12, #13                                        |
| Appendix        | Minor update         | Chapter 3 and 8–13 cross-references updated                             |

---

## Key Themes

Three themes emerged across all six decisions:

1. **The platform is a framework, not an application.** Every concept (participant types, facilitator roles, handoff artifacts, matching logic, LLM routing) must be admin-configurable per deployment. The code never hardcodes "buyer" or "seller."

2. **Trust is the product.** The platform doesn't sell transactions — it sells credible introductions. The three-layer information model, progressive communication stages, and Handoff Artifact all serve this purpose.

3. **Scope discipline.** V1 ends at handoff. Full transaction execution, fulfillment, settlement, and dispute resolution are future vertical-specific extensions. The hard problem in thin markets is finding counterparties, not executing transactions.
