# Architecture Session — Full Summary
# February 18, 2026

> **Participants:** Mustafa Uzumeri, Antigravity Agent  
> **Repositories modified:** CosolventAI (ROADMAP.md, docs/session-notes/)  
> **Continuation of:** `2026-02-18-roadmap-evolution.md` (Decisions 1–6)  
> **This file covers:** Decisions 7–11 (three-repo analysis through UI customization)

---

## Earlier Session Recap (Decisions 1–6)

The earlier session (documented in `2026-02-18-roadmap-evolution.md`) evolved the CosolventAI roadmap through six major architectural decisions:

1. **Multilateral Marketplace** — Expanded from bilateral (buyers and sellers) to three participant categories: Principals (Sellers), Principals (Buyers), and Facilitators (Service Providers). Facilitators are pulled into deals by deal requirements, not by gallery browsing.

2. **Deal Entity and Role Slots** — Introduced a Deal data model with role slots (needed → searching → proposed → confirmed → not-needed) for systematically identifying and filling facilitator roles.

3. **Two-Track Implementation Phasing** — Restructured from 6 sequential phases to a shared foundation (Phases 1–2) plus two parallel tracks: Track A (Marketplace Depth — deals, agents, pricing) and Track B (Platform Breadth — accessibility, framework, simulation).

4. **Communication Architecture** — Communication is privacy-layered and context-scoped. Five stages from gallery browsing (no contact) through selective disclosure (per-document, per-counterparty, revocable). You don't "message a user" — you communicate within a shared context.

5. **Platform Scope — Matching to Handoff** — V1 ends at handoff, not settlement. The platform's primary deliverable is the **Handoff Artifact** — a structured package (Deal Brief, Plan of Care, etc.) designed to be given to downstream professionals. The Handoff Artifact is a framework concept; each vertical defines its template.

6. **Multi-Model LLM Routing** — Real deployments need multiple LLMs simultaneously (specialized language models, vision models, embedding models, general reasoning) with task-level routing, prompt-to-model binding, and fallback chains.

---

## Decision 7: Three-Repository Architecture

### The prompt

The user asked for an architectural analysis of how the three repositories — CosolventAI, GPSimAI, and ClientSynthAI — relate to each other. What code belongs in each? How should they interact? What should the roadmaps look like for ClientSynth and GPSim given the evolved Cosolvent roadmap?

### The analysis

A thorough code review of all three repositories revealed:

- **GPSimAI** is ahead of CosolventAI in some respects — it already has all three participant types (Producer, Buyer, ServiceProvider) — but the schemas are hardcoded in Python with agricultural fields (`farmName`, `primaryCrops`, `fleetSize`, `coldChain`). It uses MongoDB + Redis, diverging from Cosolvent's PostgreSQL + pgvector.

- **ClientSynthAI** is already architecturally ready — it's a generic schema → synthetic data pipeline with multi-tenant isolation, AI-powered generation, and PDF/image creation. It just needs a Cosolvent API contract.

### The decision

The three repositories map to three distinct architectural roles:

| Layer                  | Repository    | Role                                                   | Open-source?                      |
| ---------------------- | ------------- | ------------------------------------------------------ | --------------------------------- |
| **Framework**          | CosolventAI   | Generic thin market platform infrastructure            | Yes                               |
| **Vertical**           | GPSimAI       | Agricultural trade marketplace configuration + content | No (proprietary market knowledge) |
| **Population Factory** | ClientSynthAI | Synthetic data generation for testing + Digital Twin   | Potentially                       |

**Cosolvent provides the engine. GPSim provides the fuel. ClientSynth provides the test track.**

GPSim is simultaneously the first customer of Cosolvent and the reference implementation for how to build a vertical package. When someone wants to launch Cosolvent for mental health services, they'd create their own vertical package equivalent to GPSim's role.

### What changed

- Created `docs/session-notes/2026-02-18-three-repo-architecture.md` — comprehensive analysis including what exists today, how they should relate, what belongs in each repository (with status tables), the migration path (three phases), what should NOT migrate, and roadmap themes for both ClientSynth and GPSim.

---

## Decision 8: Knowledge Slot (Fifth Slot in the Slots Architecture)

### The prompt

The user described an early GPSim feature: a chat interface where users could ask questions about the trade process. The premise was that the system sponsor would upload and curate a large collection of authoritative trade information documents — draft contracts from grain commissions, guides for container shipping of grain, import and quarantine regulations in various target countries. A buyer should be able to ask something like "what do I have to do to buy high quality malting barley from western Canada and get it delivered by container to my mill in Davao City, Philippines?" and get a useful, sourced answer.

The user noted that this level of additional information service is not relevant to Cosolvent as framework infrastructure, but is potentially very valuable to a specific vertical like agricultural trade. The goal is for the sponsor to progressively add quality information as they can find it — not a one-time data load, but a growing reference library.

### The decision

The RAG-based Q&A capability splits cleanly into framework and vertical:

- **Framework (Cosolvent):** The infrastructure — document ingestion, embedding, retrieval pipeline, domain Q&A chat interface, admin document curation UI. This is the **Knowledge Slot**, the fifth slot in the Slots Architecture.

- **Vertical (GPSim):** The content — grain commission contracts, shipping guides, quarantine regulations, quality standards. Plus the domain-specific chat prompts that define the advisor persona ("You are a trade advisor specialising in Asia-Pacific grain imports").

The Slots Architecture expanded from four to five:

| Slot          | What the framework provides                    | What the vertical provides               |
| ------------- | ---------------------------------------------- | ---------------------------------------- |
| Intelligence  | Multi-model LLM orchestration                  | Model preferences                        |
| Context       | Ingestion for *participant-supplied* documents | —                                        |
| **Knowledge** | RAG pipeline, curation UI, domain Q&A chat     | Curated reference library + chat prompts |
| Search        | Matching engine, embedding generation          | Domain-tuned matching prompts            |
| Agent         | Conversation engine, deal workflow             | Negotiation prompts, personas            |

The key distinction between Context Slot and Knowledge Slot: Context holds *participant documents* (a farmer's export certificate) that follow the three-layer privacy model. Knowledge holds *sponsor-curated reference material* (grain commission contracts) that's available to all participants and progressively built over time.

### What changed in the roadmap

- **Section 21** — Slots Architecture expanded from four to five slots. Context Slot clarified as participant-supplied documents. Knowledge Slot added with full description and example. Current state updated to note `industry_context_service` and `chatbot_service` as Knowledge Slot foundations.
- **Section 21, Required changes** — Six new Knowledge Slot items added (reference library separation, schema, metadata schema, document curation, RAG retrieval, domain Q&A, vertical-supplied prompts).
- **Three-repo architecture doc** — Updated with Knowledge Slot in framework diagram, reference library in GPSim content list, framework/vertical separation table with examples for four verticals.

---

## Decision 9: Metadata-Filtered Vector Search (Not Physical Sharding)

### The prompt

The user raised a concern about retrieval scoping. For each vertical, the curated trade knowledge library could become very large. An Indonesian buyer doesn't need to know about Japanese import regulations — the system needs to avoid polluting the context window with irrelevant reference material. The user proposed three assumptions:

1. The reference library would need to be sharded to make embedding retrieval feasible.
2. This would require a metadata schema for the library, and that schema would be vertical-specific.
3. The sharding would need to consider not only the library metadata but also link it to user metadata to minimize context size.

The user asked whether this was reasonable, or if there was a better (faster, cheaper) way to accomplish the objective.

### The decision

The user's *intent* was exactly right — scoped retrieval so irrelevant documents don't pollute the context window. But physical sharding (partitioning the library into separate segments) is the wrong mechanism. The better approach is **metadata-filtered vector search**:

- Store all documents in one `reference_library` table with `JSONB metadata` tags + `VECTOR embedding`
- At query time, apply metadata pre-filters BEFORE vector similarity ranking, in a single SQL query
- Documents can carry multiple tags (a guide to Incoterms is tagged with every destination country it applies to)
- Cross-corridor queries work naturally
- No shard management, no routing logic, no boundary problems

The user's second and third assumptions were confirmed:
- The metadata schema IS vertical-specific (agricultural trade tags are different from mental health tags)
- User metadata SHOULD automatically scope retrieval — the system injects participant context (country, role, interests, active deal corridors) as implicit filters so the user just asks their question

The user concluded that "sharding" was the wrong term for what they meant, and agreed the metadata-filtered approach was superior.

### What changed in the roadmap

- **Section 21, Knowledge Slot required changes** — Completely rewritten with the full retrieval architecture: `reference_library` table schema, vertical-specific `reference_metadata_schema` (with example tags for three verticals), metadata-filtered vector search with SQL example, automatic user-context scoping, sourced answers with citations.

---

## Decision 10: Cross-Slot Architectural Guardrails

### The prompt

The user observed that at some point down the development process, there will be a time when they want to look at buyer, seller, service provider, and industry library information as deeply synergistic — the system reasoning across participant profiles, deal context, and the reference library simultaneously. They explicitly didn't want to tackle that challenge now (except for easy wins), but they also didn't want to drive the design in any direction that would make it harder to explore later.

### The decision

The "deeply synergistic" vision was articulated concretely: a Filipino buyer asks about importing Canadian malting barley, and the system doesn't just retrieve reference documents — it also knows there are three Canadian barley exporters on the platform with matching quality grades, two freight forwarders covering Vancouver→Davao, and that the buyer's existing certifications satisfy two of the four quarantine requirements. The answer weaves all of this together.

Three architectural guardrails preserve this path at near-zero cost:

1. **Same embedding model and dimensions across all vector stores.** If `reference_library` and `participant_embeddings` use different models or dimensions, cross-collection similarity search becomes impossible without re-embedding. Both should use the Intelligence Slot's `embeddings` service config.

2. **Shared metadata vocabulary.** Geography, product categories, and certification types should use the same controlled vocabulary in both `MarketDefinition` (participant field values) and `reference_metadata_schema` (document tag values). One dropdown source, not two.

3. **Composable retrieval interface.** The retrieval layer returns results as `{source, content, metadata, score}` tuples regardless of which table they came from, with a source parameter to request from one or multiple collections.

These are design constraints, not features — they cost nothing to implement but prevent architectural decisions that would make cross-slot reasoning a migration rather than a feature addition.

### What changed in the roadmap

- **Section 21** — New subsection "Cross-slot architectural guardrails" added between Knowledge Slot requirements and Section 22, with all three guardrails documented and the rationale for future cross-collection intelligence.

---

## Decision 11: UI Customization Layers and LLM-Assisted Translation

### The prompt

The user raised the question of UI localization. Cosolvent will probably need a mechanism to support localization of the end-user interface to align with the market vertical. They saw two approaches: (1) make the support minimal and expect sponsors to do the hard work, or (2) build some basic UI customization into Cosolvent so less-skilled developers can get something up and running quickly.

In a follow-up, the user asked whether LLMs could handle the GUI translation requirements — either filling out i18n files, writing alternate UI pages, or making changes on the fly.

### The decision

Three concerns are hiding in "localization," each with a different answer:

**1. Terminology** — the highest-leverage customization. A `MarketDefinition.ui_labels` JSON map translates framework concepts to vertical-specific names ("Producer" → "Exporter" or "Practitioner", "Deal Brief" → "Plan of Care"). Incorrect terminology immediately breaks user trust. The `MarketDefinition` already configures participant types and the Handoff Artifact name, so extending it with `ui_labels` is a natural, low-cost addition. Example mappings were provided for three verticals.

**2. Language translation** — LLM-assisted, two modes:
- **UI chrome** (buttons, labels, navigation): Admin clicks "Add Filipino," the LLM generates a complete locale file in one call, the sponsor reviews and adjusts domain terms, and from that point on translations are served statically at zero incremental cost. This is an admin-time action, not a runtime service.
- **Dynamic participant content** (profile descriptions, listing text, chat messages): Runtime LLM translation via the Intelligence Slot's `translate` service, cached per content hash so each piece of content is translated exactly once.

Two approaches were explicitly rejected: translating UI strings on the fly at runtime (expensive, slow, converges to cached locale files with extra steps) and LLM-generating alternate UI pages (fragile code generation, unmaintainable).

**3. Visual branding** — CSS custom properties (colors, fonts, spacing) configurable via admin UI or theme config file. Structural customization (custom pages, domain-specific components) is the vertical's responsibility.

**Design principle:** A less-skilled developer should be able to get a branded, correctly-labelled, translated marketplace running by providing three artifacts: a `MarketDefinition` (with `ui_labels`), a locale file (LLM-generated, sponsor-reviewed), and a theme config — without forking the frontend.

### What changed in the roadmap

- **Section 21** — New subsection "UI customization layers" added with terminology table (four verticals), LLM-assisted translation workflow (both UI chrome and dynamic content), visual branding approach, and the design principle.
- **Track B, Phase B1** — New item B1.8: Build the UI customization layer (MarketDefinition.ui_labels, i18n wiring with LLM-generated locale files + admin string editor, theme tokens with CSS custom properties + admin theme config). Depends on B1.4 (dynamic participant schemas).

---

## Files Modified in This Session

| File                                                         | Change type       | Description                                                                                                              |
| ------------------------------------------------------------ | ----------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `ROADMAP.md` (Section 21)                                    | Major expansion   | Five slots (Knowledge Slot added), Knowledge Slot retrieval architecture, cross-slot guardrails, UI customization layers |
| `ROADMAP.md` (Track B1)                                      | Minor addition    | B1.8 added for UI customization layer                                                                                    |
| `docs/session-notes/2026-02-18-three-repo-architecture.md`   | Created + updated | Three-repo analysis; updated with Knowledge Slot separation, retrieval architecture, cross-vertical examples             |
| `docs/session-notes/2026-02-18-architecture-continuation.md` | Created           | This summary                                                                                                             |

---

## Key Themes Across Both Sessions (Decisions 1–11)

1. **The platform is a framework, not an application.** Every concept — participant types, facilitator roles, handoff artifacts, matching logic, LLM routing, Knowledge Slot content, UI labels — is admin-configurable per deployment. The code never hardcodes domain-specific content.

2. **Trust is the product.** The platform sells credible introductions, not transactions. The three-layer information model, progressive communication stages, Handoff Artifact, and Knowledge Slot all serve this purpose.

3. **Scope discipline.** V1 ends at handoff. The Knowledge Slot provides reference information, not transaction execution.

4. **Framework vs. vertical is the organizing principle.** Cosolvent provides mechanisms; verticals provide content. This applies to participant schemas, matching prompts, the Knowledge Slot (infrastructure vs. documents), UI labels, translations — everything.

5. **Design for synergy later without building it now.** Same embeddings, shared vocabulary, composable retrieval — three constraints that preserve the path to cross-collection intelligence at near-zero cost.

6. **LLMs are infrastructure, not just features.** Multi-model routing for different tasks, LLM-generated locale files, runtime translation with caching, domain Q&A from curated reference material — the LLM orchestration layer is a horizontal capability that powers multiple features.
