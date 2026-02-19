# Three-Repository Architecture: Cosolvent, GPSim, and ClientSynth

> **Date:** February 18, 2026  
> **Purpose:** Architectural analysis of how the three repositories relate, what belongs where, and how to build roadmaps for ClientSynth and GPSim given the evolved Cosolvent roadmap.

---

## 1. What Exists Today

### CosolventAI — The Framework
- **Tech:** Python (FastAPI) + PostgreSQL + pgvector
- **Backend services:** `admin_service`, `search_service`, `profile_service`, `llm_orchestration_service`, `industry_context_service`, `chatbot_service`
- **Frontend:** React/Next.js (admin + participant views)
- **Architecture:** Microservices with Docker Compose, shared Postgres, config-driven LLM orchestration
- **Domain coupling:** The code contains agricultural-specific schemas (`Producer`, `Exporter`, `Importer`) but has begun migrating to generic `participants` + JSONB. The roadmap calls for full generalization.

### GPSimAI — The Agricultural Marketplace Instance
- **Tech:** Python (FastAPI) + TypeScript (personalization engine) + Next.js frontend + MongoDB + Redis
- **Backend services:**
  - `profile_service` — Producer, Buyer, and **ServiceProvider** registration, file uploads, AI profile generation (domain-hardcoded schemas: `farmName`, `primaryCrops`, `certifications`, `fleetSize`, `coldChain`, etc.)
  - `personalization_engine_service` — Chat, LLM settings, FAQ generation, document processing, prompt management
  - `communication_service` — Messaging between participants
  - `notification_service` — Notifications
  - `auth_service` — Authentication
- **Frontend:** Full working UI with producer, buyer, and service provider views, admin dashboard, chat
- **Domain coupling:** **Deeply coupled to agricultural trade.** Schemas hardcode farm fields, buyer procurement fields, service provider logistics fields. This is exactly the kind of vertical-specific content that the roadmap's Slots Architecture (Section 21) aims to make configurable.

### ClientSynthAI — The Synthetic Data Generator
- **Tech:** Next.js 14 (full-stack, API routes as backend) + PostgreSQL (Supabase) + S3
- **Architecture:** Multi-tenant SaaS platform
- **Core capability:** Visual schema designer → AI-powered data generation → multi-format export
- **Key services:**
  - `AIGenerator` — Context-aware field value generation via OpenRouter
  - `JobProcessor` — Batch processing with retry, pause/resume, progress tracking
  - `ImageGenerationService` — Multi-provider image generation (Fal, OpenRouter)
  - `PDFGenerator` — AI-generated PDF documents
  - Export in CSV, JSON, XLSX, SQL
- **Domain coupling:** **None.** ClientSynth is already a generic data generation platform. It generates synthetic records from user-defined schemas. This makes it architecturally ready to serve as the synthetic data engine for any Cosolvent vertical.

---

## 2. How They Should Relate

The three repositories map to three distinct architectural roles:

```
┌──────────────────────────────────────────────────┐
│                                                    │
│   CosolventAI  — THE OPEN-SOURCE FRAMEWORK         │
│   ┌──────────────────────────────────────────┐    │
│   │  Generic platform code                    │    │
│   │  • Participants (configurable types)      │    │
│   │  • Matching engine (configurable prompts) │    │
│   │  • Communication substrate                │    │
│   │  • Deal entity + role slots               │    │
│   │  • Handoff Artifact engine (templates)    │    │
│   │  • Knowledge Slot (RAG infrastructure)    │    │
│   │  • Multi-model LLM orchestration          │    │
│   │  • Admin UI (Slots Architecture)          │    │
│   │  • Trust/privacy/audit pipeline           │    │
│   └──────────────────────────────────────────┘    │
│        │                           │               │
│        │  API contract             │  API contract  │
│        ▼                           ▼               │
│   ┌─────────────┐        ┌────────────────┐       │
│   │  GPSimAI    │        │  ClientSynthAI │       │
│   │  (Vertical) │        │  (Factory)     │       │
│   └─────────────┘        └────────────────┘       │
│                                                    │
└──────────────────────────────────────────────────┘
```

### CosolventAI = The Framework (open-source)
Everything that is **vertical-agnostic** belongs here:
- The participant data model (generic `participants` + JSONB, not `Producer`/`Buyer`/`ServiceProvider`)
- The matching engine (configurable prompts, embeddable from any schema)
- The communication substrate (scoped channels, trust stages)
- The deal entity and role slot model
- The Handoff Artifact generator engine (template-driven, not format-hardcoded)
- The multi-model LLM orchestration layer
- The admin UI (Market Definition, Intelligence Slot, Prompt Studio, field builder)
- The Knowledge Slot infrastructure (document ingestion, embedding, RAG retrieval, domain Q&A chat interface, admin document curation UI)
- The trust, verification, and privacy pipeline
- The three-layer information architecture (gallery/matching/AI-only)

### GPSimAI = A Vertical Deployment (not open-source; proprietary content)
Everything that is **agricultural-trade-specific** belongs here:
- Participant type definitions (Exporter, Importer, Customs Broker, Shipper, Inspector, Trade Finance)
- Domain-specific schemas (farm fields, crop types, certifications, logistics fields)
- Matching prompts tuned for agricultural trade (crop compatibility, seasonal availability, certification alignment)
- Handoff Artifact template: the "Deal Brief" — sections, fields, downstream consumer roles
- Domain-specific AI profiles and extraction prompts
- Regulatory context for specific trade corridors (e.g., Kenya→EU coffee export compliance)
- Communication templates and negotiation prompts specific to trade
- UI customizations (branding, vertical-specific onboarding flows)
- The "market physics" calibration for agricultural trade (seasonality parameters, shipping radii, quality standards)
- **Curated domain knowledge library:** grain commission draft contracts, container shipping guides, import/quarantine regulations for target countries, quality standards, trade finance templates. This is the content that powers the Knowledge Slot — participants browse it and ask the domain Q&A chatbot questions like "what do I need to do to buy malting barley from western Canada and ship it by container to Davao City, Philippines?"

### ClientSynthAI = The Synthetic Population Factory (open-source or separate tool)
Everything related to **generating realistic synthetic participants** to populate and test a Cosolvent deployment:
- Schema-driven synthetic data generation (already built)
- The ability to ingest a Cosolvent `MarketDefinition` and generate synthetially plausible participants that conform to it
- Scenario definitions: "generate 50 Kenyan coffee exporters, 20 European importers, 10 logistics providers"
- Behavioural scripting: synthetic participants that can "interact" with the marketplace (create listings, respond to matches, progress through deal stages) to produce testable market dynamics
- Quality scoring and variation controls
- Export to Cosolvent-compatible format (so generated data can be loaded into a Cosolvent deployment)

---

## 3. What Belongs in Each Repository

### In CosolventAI (the framework)

| Component                              | Status          | Notes                                                                                                                                   |
| -------------------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `participants` table with JSONB `data` | Exists (new)    | Needs gallery/matching profile separation                                                                                               |
| `participant_embeddings` with metadata | Exists (new)    | Needs dual embedding support                                                                                                            |
| Dynamic participant type definitions   | Not built       | Part of MarketDefinition / Slots Architecture                                                                                           |
| Deal entity + role slots               | Not built       | Roadmap A1.4-A1.7                                                                                                                       |
| Communication substrate                | Not built       | Roadmap via `communication_service` adaptation                                                                                          |
| Handoff Artifact engine                | Not built       | Roadmap A1.11 — template-driven, admin-configurable                                                                                     |
| LLM orchestration (multi-model)        | Partially built | Needs multi-provider, task routing, fallback chains                                                                                     |
| Admin UI                               | Partially built | Needs Market Definition, Prompt Studio pages                                                                                            |
| Trust/verification pipeline            | Not built       | Roadmap Phase 2                                                                                                                         |
| Matching engine (configurable)         | Partially built | `search_service` exists; needs configurable prompts                                                                                     |
| Knowledge Slot (RAG infrastructure)    | Partially built | `industry_context_service` + `documents` + `chatbot_service` exist but are not connected as a curation → embedding → RAG → Q&A pipeline |

### In GPSimAI (the agricultural vertical)

| Component                                                    | Source                                                                                      | Notes                                                                                                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Participant type config: Exporter, Importer, ServiceProvider | Currently hardcoded schemas                                                                 | Should become a `MarketDefinition` config that GPSim loads into Cosolvent                                             |
| Agricultural field schemas (farmName, primaryCrops, etc.)    | Currently hardcoded in `profile_schema.py`, `buyer_schema.py`, `service_provider_schema.py` | Should become JSON schema definitions loaded via admin UI                                                             |
| Agricultural matching prompts                                | Embedded in code                                                                            | Should move to `system_prompts` table                                                                                 |
| Trade Deal Brief template                                    | Doesn't exist yet                                                                           | Should be a Handoff Artifact template definition                                                                      |
| Testable agricultural scenarios                              | `TestCollectionGeneration/` scripts                                                         | Should eventually use ClientSynth                                                                                     |
| Domain-specific communication templates                      | Not built                                                                                   | Negotiation prompts, trade terminology                                                                                |
| Regulatory corridor data                                     | Not built                                                                                   | Trade routes, compliance requirements                                                                                 |
| Curated trade knowledge library                              | Not built                                                                                   | Grain commission contracts, shipping guides, quarantine regulations, quality standards — populates the Knowledge Slot |
| Domain Q&A chat prompts                                      | Not built                                                                                   | System prompt defining the sponsor's trade advisor persona, citation style, scope boundaries                          |

### The Knowledge Slot: Framework vs. Vertical

The Knowledge Slot is a clear example of the framework/vertical separation:

| Layer                     | What it provides                                                                                                                       | Example                                                                                                                                                         |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Framework (Cosolvent)** | Document ingestion pipeline, pgvector embedding + storage, RAG retrieval engine, domain Q&A chat interface, admin document curation UI | The infrastructure to upload, search, and answer questions from a reference library                                                                             |
| **Vertical (GPSim)**      | The documents themselves + domain-specific chat prompts                                                                                | Canadian Grain Commission contract templates, Philippine Bureau of Plant Industry quarantine requirements, ICC Incoterms guides, container shipping rate tables |

The key design point: the sponsor **progressively builds** this library over time. They start with a handful of documents and grow the knowledge base as they source authoritative reference material. The framework makes this frictionless — upload, categorise, tag, and the RAG pipeline serves it to participants immediately.

This applies to every vertical:

| Vertical                | Example Knowledge Slot content                                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Agricultural trade      | Grain standards, shipping guides, quarantine rules, trade finance templates                                        |
| Remote mental health    | Clinical guidelines, insurance coverage rules, telehealth regulations by jurisdiction, cultural sensitivity guides |
| Specialty manufacturing | Materials specs, quality standards (ISO, ASTM), IP protection frameworks, export control regulations               |
| Art / collectibles      | Authentication standards, provenance documentation requirements, insurance guides, import duty schedules           |

### In ClientSynthAI (the synthetic data factory)

| Component                   | Status    | Notes                                                                                                     |
| --------------------------- | --------- | --------------------------------------------------------------------------------------------------------- |
| Visual schema designer      | Built     | Ready to use                                                                                              |
| AI-powered field generation | Built     | Context-aware, with examples                                                                              |
| Multi-format export         | Built     | CSV, JSON, XLSX, SQL                                                                                      |
| Image generation            | Built     | Multi-provider                                                                                            |
| PDF document generation     | Built     | Content-aware                                                                                             |
| Cosolvent API contract      | Not built | Need to define how ClientSynth receives a MarketDefinition and produces Cosolvent-compatible participants |
| Scenario definitions        | Not built | "Generate N participants of type X with distribution Y"                                                   |
| Behavioural scripting       | Not built | Synthetic participant "behaviour" for market simulation                                                   |
| Digital Twin integration    | Not built | Drives the simulation harness (Roadmap B2.3)                                                              |

---

## 4. The Migration Path

### Phase 1: Separate concerns

**Current problem:** GPSimAI contains both framework code and vertical content, intermingled. Its `profile_service` is both a generic participant store (registration flow, file uploads, AI profile generation) and a domain-specific schema definition (farm fields, buyer fields, logistics fields).

**Action:**
1. **In CosolventAI:** Complete the migration from hardcoded `Producer` schemas to generic `participants` + JSONB. Build the `MarketDefinition` model that lets an admin define participant types and their fields. (Roadmap Phase 1, items 1.1-1.2, and Section 21)
2. **In GPSimAI:** Extract the agricultural schemas (producer fields, buyer fields, service provider fields) into a `MarketDefinition` config file (JSON/YAML). This config becomes the "agricultural trade vertical package" — the thing that turns a bare Cosolvent instance into a trade marketplace.
3. **In both:** Define the API contract by which GPSim loads its vertical configuration into Cosolvent. This is the `MarketDefinition` API.

### Phase 2: Connect ClientSynth

**Current problem:** ClientSynth is a standalone SaaS product. It generates generic synthetic data from user-defined schemas. It has no awareness of Cosolvent's participant model, matching logic, or deal flow.

**Action:**
1. **Define the Cosolvent ↔ ClientSynth API contract** (Roadmap B2.1). ClientSynth needs to be able to:
   - Receive a `MarketDefinition` (participant types, field schemas)
   - Generate synthetic participants that conform to it
   - Export them in a format Cosolvent can ingest
2. **Build scenario definitions.** Instead of generating random records, generate contextually rich synthetic populations: "50 small-scale Ethiopian coffee producers in Sidama region with organic certification" or "15 logistics companies covering East Africa with cold chain capability."
3. **This does NOT require merging the repositories.** ClientSynth remains a separate tool that produces data for Cosolvent. The integration point is an API or export format.

### Phase 3: Digital Twin

**Current problem:** No simulation capability exists anywhere.

**Action:**
1. Build the Digital Twin harness (Roadmap B2.3) — this lives in CosolventAI as a framework capability
2. The harness combines: a Cosolvent instance + a ClientSynth population + market physics parameters
3. GPSimAI provides the first real set of market physics parameters (agricultural trade dynamics) for calibration
4. The simulation runs matching, deal assembly, and handoff artifact generation to test whether the market model works before deploying to real users

---

## 5. What Should NOT Migrate

Some things in GPSimAI should stay there and not move to Cosolvent, because they are valuable vertical content:

| Component                                                                                    | Why it stays in GPSim                                                                                                                                                                    |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ServiceProviderRegisterSchema` fields (fleetSize, coldChain, vehicleTypes, storageCapacity) | These are logistics-domain fields. A mental health marketplace would have entirely different service provider fields.                                                                    |
| Agricultural matching logic (crop compatibility, seasonal overlap, certification alignment)  | This is domain knowledge, not framework code                                                                                                                                             |
| `TestCollectionGeneration/` scripts                                                          | These are agricultural-specific synthetic data generators — precursors to what ClientSynth will do generically                                                                           |
| Communication templates for trade negotiation                                                | Domain-specific prompts                                                                                                                                                                  |
| `personalization_engine_service` (as currently built)                                        | This service is tightly coupled to GPSim's MongoDB data model. Cosolvent has its own `chatbot_service` and `llm_orchestration_service` with a different architecture (PostgreSQL-backed) |

### Technology divergence note

GPSimAI uses **MongoDB + Redis** while CosolventAI uses **PostgreSQL + pgvector**. This is a significant divergence. When GPSim eventually runs on Cosolvent, the data layer will shift to PostgreSQL. The MongoDB schemas in GPSim should be treated as **domain knowledge documentation** (what fields does an agricultural marketplace need?) rather than final data models.

---

## 6. Toward Roadmaps for ClientSynth and GPSim

### ClientSynth Roadmap — Key Themes

1. **Cosolvent-aware generation.** Accept a `MarketDefinition` and produce conformant synthetic participants. This is the Cosolvent ↔ ClientSynth API contract.
2. **Scenario-based generation.** Move from "generate N records from this schema" to "generate a demographically and economically plausible population for this market." This requires: (a) distribution controls (geographic, size, certification mix), (b) inter-record consistency (a region with 50 coffee farms should also have 3-5 logistics providers and 1-2 customs brokers), (c) cultural and naming coherence.
3. **Behavioural scripting.** Generate not just static profiles but behavioural scripts: "this producer lists 500 bags of Grade 1 coffee every October; this buyer looks for East African coffee with organic cert; this logistics provider covers Mombasa-Rotterdam." These scripts drive the Digital Twin.
4. **Document generation.** Generate realistic supporting documents (certificates, invoices, compliance documents) that can be attached to synthetic participants. ClientSynth already has PDF generation — this extends it with domain-aware templates.
5. **Quality scoring for market realism.** Beyond individual record quality, score the population for market-level plausibility: "Is this population consistent with what a real agricultural market would look like? Are there enough facilitators relative to principals? Are the geographic distributions realistic?"

### GPSim Roadmap — Key Themes

1. **Extract vertical content from code to configuration.** Move agricultural schemas, matching prompts, and business rules from hardcoded Python/TypeScript into `MarketDefinition` configs and `system_prompts` entries.
2. **Define the agricultural Deal Brief template.** This is the first real Handoff Artifact template — what sections does a cross-border agricultural trade deal need? What information flows from participants, matches, and conversations into the brief?
3. **Build agricultural regulatory context.** Trade corridors, compliance requirements, certification standards per route. This becomes the knowledge base that the AI uses to flag regulatory considerations in matching and deal assembly.
4. **Calibrate market physics.** Define the physics parameters for agricultural trade: seasonality curves, quality grade hierarchies, economic shipping radii, cold chain requirements. These parameters drive both matching logic and Digital Twin simulation.
5. **Agricultural communication templates.** Negotiation prompts, trade terminology glossaries, document templates (phytosanitary certificates, bills of lading, letters of credit outlines) specific to agricultural trade.
6. **First Digital Twin scenario.** Use ClientSynth to generate a synthetic population + GPSim vertical config + Cosolvent framework = a runnable simulation of, say, the East African coffee-to-Europe trade corridor.

---

## 7. Summary: The Clean Separation

| Layer                  | Repository    | Role                                                   | Open-source?                      |
| ---------------------- | ------------- | ------------------------------------------------------ | --------------------------------- |
| **Framework**          | CosolventAI   | Generic thin market platform infrastructure            | Yes                               |
| **Vertical**           | GPSimAI       | Agricultural trade marketplace configuration + content | No (proprietary market knowledge) |
| **Population Factory** | ClientSynthAI | Synthetic data generation for testing + Digital Twin   | Potentially (generic tool)        |

The key insight: **Cosolvent provides the engine. GPSim provides the fuel. ClientSynth provides the test track.**

When someone wants to launch Cosolvent for a different vertical (mental health delivery, art collectibles, specialty manufacturing), they:
1. Take the CosolventAI framework
2. Create their own vertical package (equivalent to GPSim's role)
3. Use ClientSynth to generate a test population
4. Run a Digital Twin to validate the market model
5. Deploy

GPSim is simultaneously the **first customer** of Cosolvent and the **reference implementation** for how to build a vertical package.
