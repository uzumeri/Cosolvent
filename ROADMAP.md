# CosolventAI ↔ Whitepaper Alignment Roadmap

> **Source whitepaper:** `tm-reference-CL4_V2.md` — *Thin Markets: A Deep Dive into Market Physics and Engineering*
> **Repository assessed:** CosolventAI v0.1 Beta (this repo)
> **Date:** 2026-02-14

---

## Executive Summary

The whitepaper describes a **ten-force "market physics"** framework plus an extensive suite of **AI-driven market engineering** interventions. CosolventAI's current implementation covers a **narrow vertical slice** of that vision — primarily producer (exporter) profiling, vector-based semantic search, basic LLM orchestration, and a rudimentary chatbot. The whitepaper's scope is significantly broader: it calls for dynamic pricing, asynchronous brokerage agents, trusted intermediation with confidential data, multimodal input translation, user aggregation, dispute resolution, progressive trust infrastructure, synthetic market bootstrapping, and a full buyer/importer side of the marketplace.

This document catalogues the gaps and describes — in conceptual, non-code terms — the changes required to bring CosolventAI into alignment with the whitepaper.

---

## Table of Contents

1. [Market Physics Model — Missing Domain Concepts](#1-market-physics-model--missing-domain-concepts)
2. [Bilateral Marketplace — The Missing Buyer/Importer Side](#2-bilateral-marketplace--the-missing-buyerimporter-side)
3. [Semantic Matching & AI-Driven Discovery](#3-semantic-matching--ai-driven-discovery)
4. [Trusted Intermediation & Confidential Matching](#4-trusted-intermediation--confidential-matching)
5. [Asynchronous Brokerage Agents](#5-asynchronous-brokerage-agents)
6. [Dynamic Pricing and fair-Value Engine](#6-dynamic-pricing-and-fair-value-engine)
7. [Multimodal Input Translation & Accessibility](#7-multimodal-input-translation--accessibility)
8. [User Aggregation](#8-user-aggregation)
9. [Trust & Safety Infrastructure](#9-trust--safety-infrastructure)
10. [Institutional Memory & Contextual Persistence](#10-institutional-memory--contextual-persistence)
11. [Synthetic Market Bootstrapping](#11-synthetic-market-bootstrapping)
12. [Dispute Resolution](#12-dispute-resolution)
13. [Psychological Framing & Personalization](#13-psychological-framing--personalization)
14. [Regulatory & Compliance Layer](#14-regulatory--compliance-layer)
15. [Geographic & Temporal Distance Awareness](#15-geographic--temporal-distance-awareness)
16. [Fulfillment & Settlement Integration](#16-fulfillment--settlement-integration)
17. [Industry Context Service Enhancements](#17-industry-context-service-enhancements)
18. [Frontend & UX Gaps](#18-frontend--ux-gaps)
19. [Data Model & Schema Evolution](#19-data-model--schema-evolution)
20. [Infrastructure & Operations](#20-infrastructure--operations)
21. [Prioritised Implementation Phases](#21-prioritised-implementation-phases)

---

## 1. Market Physics Model — Missing Domain Concepts

### What the whitepaper says
The framework identifies **ten forces** (Desire to Exchange, Opacity & Friction, Physical Distance, Temporal Distance, Information Density, Fulfillment Options, Friction-Free Market Size, Trust & Safety, Cognitive Bandwidth, Regulatory Friction) and asserts that every marketplace should **measure** each force for its target market segment before engineering interventions.

### Current state in CosolventAI
There is **no explicit representation** of these forces anywhere in the codebase. The data models (`producers`, `embeddings`, `profiles`) carry some implicit signals — `region`, `certifications`, `primary_crops` — but there is no structured way to quantify or reason about market forces.

### Required changes
- **Introduce a "Market Physics Scorecard" domain model.** Each marketplace vertical (or sub-market) should have a persisted assessment of the ten forces, with numeric or categorical ratings. This drives which engineering interventions the platform activates.
- **Add a diagnostic tool** (possibly an admin-facing wizard or a prompt-driven analysis) that, given a description of a market segment, generates an initial scorecard using LLM analysis.
- **Wire the scorecard into the search and matching logic** so that the system can weight matching dimensions differently depending on which forces are dominant. For example, in a market where temporal distance is the primary challenge, the matching engine should prioritize availability windows and urgency signals over geographic proximity.

---

## 2. Bilateral Marketplace — The Missing Buyer/Importer Side

### What the whitepaper says
A functioning marketplace requires **both buyers and sellers** with rich, structured profiles. The whitepaper discusses importer profiles, procurement needs, and match-making between the two sides at length.

### Current state in CosolventAI
The system is overwhelmingly **seller/producer-centric**. The database schema (`producers` table, `ProducerRegisterSchema`, `ProducerSchema`) has detailed fields for farms and exporters. The `ImporterProfileSchema` exists only as a lightweight Pydantic model in the LLM orchestration config — it is never persisted, never exposed through a route, and has no corresponding database table.

The `search_service` searches for producers only. There is no concept of a "buyer query profile" being matched against a pool of sellers, nor any mechanism for sellers to discover buyer demand.

### Required changes
- **Create a full `buyer_service` (or extend the profile_service)** with buyer/importer registration routes, CRUD operations, and a database table mirroring the richness of the producer table but tailored to buyer needs (procurement requirements, budget ranges, volume needs, quality specifications, delivery windows, regulatory requirements).
- **Extend the search service for bidirectional matching.** Buyers should be able to search for sellers, and sellers should be able to search for buyers. The `embeddings` table needs to support both entity types, or a second set of embeddings should be maintained.
- **Build buyer-side frontend views.** The current landing page and admin pages are producer-focused. A buyer dashboard, buyer registration flow, and buyer search interface are needed.

---

## 3. Semantic Matching & AI-Driven Discovery

### What the whitepaper says
AI should enable **"preserving heterogeneity while enabling discovery"** — the core breakthrough. Instead of forcing standardisation, vector embeddings and semantic matching allow complex, unique items to be matched to specific needs. The whitepaper describes generative preference elicitation (conversational discovery of needs) and semantic matching against high-dimensional representations.

### Current state in CosolventAI
- The `search_service` uses **pgvector** for cosine similarity search over producer embeddings — this is a strong foundation.
- Embeddings are currently generated from the producer's `ai_profile` text only. Metadata filtering is limited to region, certifications, and primary crops as simple text/array matches.
- The `QueryRequest` schema accepts a free-text `query` string, which is a basic form of semantic search. However, there is no **conversational preference elicitation** — the chatbot in `frontend/components/chatbot/chatbot.tsx` appears to be a general Q&A bot against the industry context, not a structured matching assistant.
- There is no **match explanation or rationale** returned with results. The `ProducerSimilarity` response contains only `producer_id` and `score`.

### Required changes
- **Enrich embeddings with multi-signal input.** The text embedded should combine the AI profile with structured metadata (certifications, region, crop types, export experience, farm description) in a structured template, not just the raw `ai_profile` string. This preserves the heterogeneity the whitepaper emphasises.
- **Implement generative preference elicitation.** Build a conversational interface (extending the existing chatbot) that progressively asks buyers clarifying questions, constructs a detailed requirement vector, and runs semantic search against it. The whitepaper explicitly calls this out as replacing "50 filter fields" with a natural conversation.
- **Add match rationale generation.** When search results are returned, use the LLM to generate a brief explanation of *why* each result is a good fit, referencing specific attributes. This maps to the whitepaper's "contextual explanation" capability.
- **Introduce multi-vector matching.** Instead of a single embedding per profile, consider separate embeddings for different facets (product quality, logistics capability, certification alignment) and composite scoring.

---

## 4. Trusted Intermediation & Confidential Matching

### What the whitepaper says
This is identified as one of the **three core AI capabilities** (Capability 2). AI can learn confidential information from both parties and facilitate matches without requiring mutual disclosure. The buyer shares their true budget and strategic priorities; the seller shares actual capabilities and pricing flexibility. The AI determines fit without exposing either party's sensitive data to the other.

### Current state in CosolventAI
There is **no concept of confidential information handling.** All profile data is stored in a single `producers` table and is presumably accessible to admin users. There is no mechanism for a buyer to submit private requirements, no confidentiality envelope, and no AI intermediary that operates on data that neither side can see directly.

### Required changes
- **Design a "confidential data vault" pattern.** Both buyers and sellers should be able to submit sensitive information (budget ranges, capacity constraints, strategic priorities) that is stored encrypted and only accessible to the AI matching engine — never exposed in search results, admin panels, or to the counterparty.
- **Build a confidential matching pipeline.** The LLM-driven matching step should be able to read from both the public profile and the confidential vault, evaluate fit, and produce a match recommendation that reveals only that a match exists — not the underlying sensitive data.
- **Implement structured disclosure gates.** After a match is suggested, both parties should opt in to progressively share more information (aligning with the whitepaper's "trust gradations" concept from Chapter 34).

---

## 5. Asynchronous Brokerage Agents

### What the whitepaper says
AI should act as an **"always-on negotiator"** representing each party even when offline. This addresses temporal distance. The AI maintains conversation state across sessions and time zones, answers detailed questions, negotiates within pre-set boundaries, and escalates to humans when needed.

### Current state in CosolventAI
The chatbot component is a **stateless Q&A interface**. The `industry_context_service` has a `chatAgent.ts` and `chatService.ts`, but these are general RAG chat services — not autonomous agents with delegated authority. There is no concept of an agent acting on behalf of a user, no negotiation parameters, and no asynchronous deal progression.

### Required changes
- **Introduce a "User Agent" entity.** Each seller (and eventually each buyer) should be able to configure an AI agent with:
  - Pre-approved negotiation parameters (price ranges, minimum order sizes, delivery windows)
  - Authority levels (what the agent can agree to autonomously vs. what requires human approval)
  - Personality/communication guidelines
- **Build an asynchronous conversation engine.** When a counterparty initiates contact, the agent should be able to carry on a multi-turn conversation across days, maintain state, and escalate appropriately.
- **Add a "deal progression" workflow** that tracks conversations from initial inquiry through qualification, negotiation, deal structuring, and human approval.
- **Build a notification system** so that when an agent reaches a decision boundary or needs human input, the owner is alerted via email, SMS, or in-app notification.

---

## 6. Dynamic Pricing and Fair-Value Engine

### What the whitepaper says
AI should calculate **"fair theoretical value"** in real time, synthesising comparable sales data, intrinsic value metrics, and market conditions. This eliminates the opacity that prevents buyers from knowing if a price is fair, directly addressing the "market for lemons" problem. The whitepaper gives the specialty grain pricing example: analyzing 2,300 comparables and proposing a credible value range.

### Current state in CosolventAI
There is **no pricing module whatsoever**. No price fields exist in the producer schema, no transaction history is stored, and no valuation logic is present.

### Required changes
- **Add pricing and transaction history data models.** The database needs tables for listings (with asking prices), completed transactions (with actual prices), and market reference data.
- **Build a fair-value estimation service.** This service should:
  - Ingest comparable transaction data (initially seeded, later populated from actual marketplace transactions)
  - Adjust for quality attributes, location, seasonality, and volume
  - Produce a confidence-banded price estimate (e.g., "fair value: $412–428/tonne")
- **Integrate the pricing engine into the matching flow.** When a match is suggested, include a fair-value estimate so both parties have a credible, neutral anchor.

---

## 7. Multimodal Input Translation & Accessibility

### What the whitepaper says
This is identified as **Core Capability 3**. AI should accept information in any natural form — voice, photos, casual text, WhatsApp messages, handwritten invoices — and translate it into structured marketplace data. The Ethiopian coffee farmer example is central: a farmer calls a phone number, describes their product in Amharic, and the AI generates a marketplace listing.

### Current state in CosolventAI
- The LLM orchestration service has `metadata_extraction.py` with **placeholder** functions for `image_to_text` and `speech_to_text`. Both return hardcoded placeholder strings.
- There is a `translate.py` service that can translate text via LLM, which is a start.
- The frontend requires structured form input for producer registration. There is no voice input, no photo-based listing creation, and no low-literacy accommodation.

### Required changes
- **Implement real image-to-text (VLM) pipeline.** Replace the placeholder in `metadata_extraction.py` with a working vision-language model integration. This should accept photos of products, farms, documents, or handwritten invoices and extract structured data.
- **Implement speech-to-text pipeline.** Integrate a real STT model (e.g., Whisper) to replace the placeholder. This should support multiple languages.
- **Build a "natural language listing creation" flow.** A user should be able to describe their product in conversational text (typed or spoken), and the system should auto-generate a structured listing with appropriate fields filled in. The existing `profile_generation.py` already does something similar for AI profile generation — this pattern should be extended to listing creation.
- **Add WhatsApp/SMS integration** as an interface layer, particularly for deployment contexts where web access is limited (consistent with the whitepaper's focus on developing-market participants).

---

## 8. User Aggregation

### What the whitepaper says
Many potential market participants are individually too small to be commercially relevant. AI should facilitate aggregating small participants into collective units. The Ethiopian Cold Chain Cooperative example: 50 smallholders producing 50–200 kg/week are aggregated by AI into commercially meaningful lots.

### Current state in CosolventAI
There is **no aggregation concept.** Each producer is an independent entity with no support for cooperatives, groups, or collective listings.

### Required changes
- **Add a "Group/Cooperative" entity** that can contain multiple producer profiles. The group should have its own profile, aggregate production data, and a combined listing.
- **Build aggregation logic** that:
  - Sums individual production volumes into commercially relevant lots
  - Evaluates and sorts quality across members
  - Manages revenue/price allocation back to individual contributors
- **Expose cooperative management in the admin and user frontends.**

---

## 9. Trust & Safety Infrastructure

### What the whitepaper says
Trust is not binary — it operates on a **gradient** (browsing → profile creation → sharing sensitive data → initiating contact → negotiating → committing funds → ongoing relationship). The platform must provide appropriate trust mechanisms at each stage. Trust also encompasses platform trust (is the algorithm fair?), counterparty trust (is this entity reliable?), and transaction trust (will the deal settle?).

Specific mechanisms called out include: profile verification, reputation inference, risk assessment, transparent matching, progressive trust building (6-stage model), and evidence-based "Trust-as-a-Service" dossiers.

### Current state in CosolventAI
- There is a simple `status` field on the producer record (e.g., "approved") — this is the **only trust signal** in the system.
- The admin service can presumably approve/reject producers, which is a manual gate.
- There is no verification pipeline, no reputation tracking, no risk scoring, no progressive disclosure mechanism, and no dispute history.

### Required changes
- **Implement a verification pipeline.** When a producer registers, the system should:
  - Auto-check document consistency (e.g., does the certification document match claimed certifications?)
  - Cross-reference with external data sources where possible
  - Assign a verification score
- **Build a reputation system.** Track successful transactions, dispute rates, response times, and counterparty ratings. Aggregate these into a "trust score" visible to counterparties (with appropriate privacy controls).
- **Implement the 6-stage progressive trust model** described in the whitepaper (anonymous browsing → verified profile → guided introduction → structured information exchange → protected transaction → post-transaction evaluation).
- **Add escrow and settlement primitives** or integrate with existing payment/settlement services (letters of credit, escrow APIs).
- **Build transparent matching.** When the AI suggests a match, surface the reasoning — which factors drove the match quality score.

---

## 10. Institutional Memory & Contextual Persistence

### What the whitepaper says
AI should maintain institutional memory — remembering the nuance of why a deal failed, tracking evolving preferences, recognising patterns across interactions, and moving from "search" to "anticipation."

### Current state in CosolventAI
- The `industry_context_service` ingests documents and makes them available for RAG chat — this is a form of **domain knowledge memory**.
- However, there is **no per-user interaction memory.** The system does not track past searches, past match rejections and their reasons, evolving preference patterns, or conversation histories tied to specific users.

### Required changes
- **Add a user interaction log.** Store every search query, match view, match rejection (with optional reason), and conversation turn, linked to the user.
- **Build a preference evolution model.** Periodically (or on-demand) analyze a user's interaction history to identify emerging patterns, converging requirements, and changing priorities.
- **Enable "anticipatory matching."** When new listings or counterparties appear that match an inferred (not explicitly stated) evolving need, proactively notify the user.
- **Store deal outcome data.** For completed transactions, record whether it succeeded, what went well, what went wrong, and use this to refine future matching for similar participants.

---

## 11. Synthetic Market Bootstrapping

### What the whitepaper says
To solve the cold-start problem, AI should construct **synthetic demand signals** (from industry reports, procurement notices, trade data, job postings) and **synthetic supply inventories** (from farm reports, industrial output data, government statistics) to demonstrate market viability before real participants have joined.

### Current state in CosolventAI
There is **no bootstrapping mechanism.** The marketplace requires manual producer registration and provides no synthetic supply/demand signals.

### Required changes
- **Build a data ingestion pipeline for external market intelligence.** The `industry_context_service` already ingests documents — extend this to ingest structured trade data feeds, government agricultural statistics, procurement notices, and industry reports.
- **Create "synthetic profiles" from external data.** These would represent known market participants (drawn from public records) who have not yet registered, showing potential counterparties that a market exists.
- **Build an outreach engine.** When a synthetic match is identified, generate personalised outreach messages (per Chapter 24 of the whitepaper) to attract the identified potential participants onto the platform.

---

## 12. Dispute Resolution

### What the whitepaper says
AI should provide automated dispute triage (classifying by severity), AI-assisted evaluation, and predictive dispute prevention (identifying high-risk transactions before they occur).

### Current state in CosolventAI
There is **no dispute resolution system** of any kind.

### Required changes
- **Add a disputes data model and service.** Allow either party to file a claim, attach evidence, and describe the issue.
- **Build an AI triage system** that classifies disputes, suggests resolutions for minor issues, and escalates complex cases to human mediators with full context prepared.
- **Implement predictive risk scoring** on transactions — flag deals with patterns historically associated with disputes (communication anomalies, vague contract terms, unusual volumes).

---

## 13. Psychological Framing & Personalization

### What the whitepaper says
AI should perform psychographic profiling of users and dynamically frame messages to match their psychology — risk-averse users see safety and guarantees messaging, opportunistic users see upside and scarcity messaging, etc.

### Current state in CosolventAI
There is **no personalisation of any kind.** All users see the same content, same messaging, and same interface.

### Required changes
- **Add behavioural analytics tracking.** Monitor user interaction patterns (browse time, click patterns, conversation style, purchase history).
- **Build a psychographic profiling module** that classifies users into communication style categories.
- **Implement dynamic message framing** in the chatbot, match notifications, and listing displays. This is primarily a prompt-engineering task layered onto the existing LLM orchestration service.

---

## 14. Regulatory & Compliance Layer

### What the whitepaper says
Regulatory friction fragments markets. The whitepaper emphasises understanding which regulatory regimes apply, providing compliance tooling, and adapting to different jurisdictions. The Middle Powers coalition's standards alignment strategy is a core theme.

### Current state in CosolventAI
There is **no regulatory awareness.** The system has a `country` field on the producer record and nothing else. No compliance checks, no standards verification, no cross-border regulatory guidance.

### Required changes
- **Add a regulatory context module.** For each market vertical and jurisdiction pair, maintain a knowledge base of relevant regulations, standards requirements, and compliance procedures.
- **Integrate regulatory checks into matching.** When matching a Canadian exporter with an EU buyer, automatically flag relevant regulatory requirements (GDPR for data, CE marking for products, CETA provisions for trade).
- **Build a compliance checklist generator** that, given a match between two parties in different jurisdictions, produces a structured list of regulatory steps required to complete the transaction.

---

## 15. Geographic & Temporal Distance Awareness

### What the whitepaper says
Physical distance and temporal distance are **distinct forces** requiring different engineering solutions. Physical distance is addressed by logistics optimisation; temporal distance is addressed by storage, futures, and asynchronous brokerage. The whitepaper insists these must not be conflated.

### Current state in CosolventAI
- The `region` field on profiles and embeddings provides **minimal geographic awareness** — it is a text field, not a geo-coordinate.
- There is **no temporal awareness at all.** No availability windows, no harvest seasonality, no time-zone handling, no concept of "when is this product available?"

### Required changes
- **Add geolocation data.** Store coordinates (lat/long) for producers and buyers. Use this for logistics cost estimation and geographic distance calculations.
- **Add temporal availability models.** Each listing should have production/availability windows (e.g., "harvest: September–October", "available for shipment: November–March"). Buyers should specify desired delivery windows.
- **Build temporal matching.** The matching engine should consider whether buyer demand windows and seller supply windows overlap, and flag temporal gaps that require storage, forward contracting, or other engineering.
- **Add time-zone-aware communication** to the asynchronous brokerage agents (Section 5 above).

---

## 16. Fulfillment & Settlement Integration

### What the whitepaper says
Fulfillment options — transportation costs, cold chain requirements, economic shipping radii, settlement mechanisms — are a fundamental market physics force. The platform should integrate with logistics and settlement infrastructure.

### Current state in CosolventAI
There is **no fulfillment or settlement integration.** The system ends at "here is a matched profile."

### Required changes
- **Add logistics estimation.** Given a matched buyer-seller pair, estimate shipping costs, identify optimal transport modes, and flag any cold-chain or special handling requirements.
- **Integrate payment/settlement primitives.** At minimum, support generating letters of credit outlines, escrow instructions, or integration with payment APIs.
- **Model economic shipping radii.** For each product type, define the geographic range within which shipping is economically viable, and use this as a hard filter or scoring input in matching.

---

## 17. Industry Context Service Enhancements

### What the whitepaper says
The platform needs deep domain knowledge — including market intelligence, commodity specifications, grading systems, certification requirements, and industry-specific terminology — to enable effective matching and trusted intermediation.

### Current state in CosolventAI
The `industry_context_service` is the **most mature** component relative to the whitepaper's vision. It already ingests documents, generates embeddings, stores them in pgVector, and exposes a RAG-based chat interface. The worker pipeline (BullMQ-based) handles async document processing.

### Required changes
- **Expand ingestion sources.** Beyond uploaded documents, ingest structured feeds — commodity pricing APIs, trade statistics, regulatory databases, certification registries.
- **Build domain-specific ontologies.** For each vertical (e.g., agriculture), maintain a structured knowledge graph of product types, quality grades, certifications, and their relationships.
- **Connect industry context to matching.** The current industry context lives in the chat service but is not wired into the search/matching pipeline. The matching engine should use industry context to understand that "CWRS #1" is a wheat grade, that "protein content > 13%" implies a premium product, etc.

---

## 18. Frontend & UX Gaps

### What the whitepaper says
The interface should respect cognitive bandwidth, provide curated (not overwhelming) results, support multiple modalities (web, mobile, voice, SMS), and progressively disclose information aligned with trust levels.

### Current state in CosolventAI
- The landing page is marketing-focused (Hero, How It Works, Live Offerings, Producers sections).
- The protected area has a user page and an admin page — both appear minimal.
- The chatbot is a floating widget.
- There is no mobile-specific UX, no voice interface, and no low-bandwidth mode.

### Required changes
- **Build a buyer dashboard** with search, saved searches, match notifications, and deal tracking.
- **Build a seller dashboard** with listing management, incoming inquiries, agent configuration, and analytics.
- **Redesign the matching UX** to show rich match cards with AI-generated rationales, fair-value estimates, and trust scores rather than just ranked IDs.
- **Add progressive disclosure** — initial match results show minimal information; users can "unlock" more detail as they progress through trust levels.
- **Plan for mobile-first and low-bandwidth interfaces** (the whitepaper emphasises voice-first interaction and SMS for developing markets).

---

## 19. Data Model & Schema Evolution

### Current gaps summarised

The `init.sql` schema reveals a producer-only marketplace. The following tables or concepts are **absent** and needed:

| Missing Concept               | Description                                                                                               |
| ----------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Buyers / Importers**        | Full buyer profiles with procurement needs, quality specifications, volume requirements, delivery windows |
| **Listings**                  | Specific offerings from sellers with pricing, availability windows, quantity, quality specs               |
| **Transactions**              | Completed deals with prices, ratings, and outcome tracking                                                |
| **Deals / Negotiations**      | In-progress conversations between matched parties, with status tracking                                   |
| **Confidential Vaults**       | Encrypted storage for sensitive buyer/seller information used only by AI                                  |
| **User Agents**               | Configuration for autonomous AI agents (negotiation parameters, authority levels)                         |
| **Interaction Logs**          | User search history, match views, rejections, conversation history                                        |
| **Disputes**                  | Dispute records with evidence, status, and resolution                                                     |
| **Cooperatives / Groups**     | Multi-producer aggregation entities                                                                       |
| **Regulatory Rules**          | Jurisdiction-specific compliance requirements                                                             |
| **Trust Scores**              | Computed reputation scores and verification status                                                        |
| **Market Physics Scorecards** | Per-vertical assessment of the ten forces                                                                 |

---

## 20. Infrastructure & Operations

### Current state
The infrastructure (Docker Compose, Postgres with pgvector, Redis, RabbitMQ, MinIO, Nginx reverse proxy) is well-designed for the current scope.

### Required changes for whitepaper alignment
- **Add a notification service** (email, SMS, push) for agent escalations, match alerts, and deal updates.
- **Add a scheduled job runner** for periodic tasks: synthetic bootstrapping scans, reputation recalculation, preference evolution analysis, and predictive risk scoring.
- **Consider adding a dedicated vector database** (or tuning pgvector configuration) as embedding volumes grow with bidirectional profiles, multi-vector representations, and interaction logs.
- **Plan for multi-tenancy** — the whitepaper envisions the framework being applicable across different verticals. The current implementation is hardcoded for agricultural producers.
- **Add API gateway capabilities** (rate limiting, API keys, usage tracking) as the platform exposes more services to external integrations (WhatsApp bots, SMS gateways, payment APIs).

---

## 21. Prioritised Implementation Phases

Based on the whitepaper's emphasis on which capabilities are most transformative, the following phasing is recommended:

### Phase 1 — Bilateral Foundation (Critical Path)
*Addresses: Chapters 1–2, 7, 19–20*

1. Build the buyer/importer side — data model, service, registration, dashboard
2. Implement bidirectional semantic search (buyers search sellers, sellers search buyers)
3. Enrich embedding generation with multi-signal structured templates
4. Add match rationale generation to search results
5. Add listings with pricing, availability, and quantity fields

### Phase 2 — Trust & Matching Depth
*Addresses: Chapters 10, 32–35, 19–20, 27*

6. Implement progressive trust model (6-stage) with verification pipeline
7. Build confidential data vault and AI-only matching access
8. Add reputation tracking and trust scoring
9. Implement generative preference elicitation (conversational search)
10. Add transparent matching explanations

### Phase 3 — Temporal & Autonomous Capabilities
*Addresses: Chapters 6, 22, 26*

11. Add temporal availability models and temporal matching
12. Build asynchronous brokerage agents with configurable authority
13. Add institutional memory — user interaction logs and preference evolution
14. Build notification service for agent escalations and match alerts
15. Implement deal progression workflow

### Phase 4 — Market Intelligence & Pricing
*Addresses: Chapters 23, 25, 29*

16. Build fair-value estimation engine
17. Add transaction history data model
18. Implement synthetic market bootstrapping from external data
19. Expand industry context ingestion to structured feeds
20. Build user aggregation / cooperative support

### Phase 5 — Accessibility & Reach
*Addresses: Chapters 28, 30–31*

21. Implement real VLM and STT pipelines (replacing placeholders)
22. Build natural-language listing creation (voice/text to structured listing)
23. Add WhatsApp/SMS interface layer
24. Implement dynamic psychological framing
25. Build dispute resolution system with AI triage

### Phase 6 — Regulatory & Global Scale
*Addresses: Chapters 5, 8, 12*

26. Add geolocation and logistics estimation
27. Build regulatory context module and compliance checklist generator
28. Implement fulfillment and settlement integration
29. Add multi-tenancy for cross-vertical deployment
30. Build the Market Physics Scorecard diagnostic tool

---

## Cross-Cutting Concerns

Across all phases, the following principles from the whitepaper should guide implementation:

- **Never destroy information through premature standardisation.** Preserve heterogeneity in profiles and listings; let AI handle the complexity of matching.
- **Design for cognitive bandwidth constraints.** Every UI and API should present curated, relevant subsets — not raw data dumps.
- **Remember that trust is the prerequisite, not a feature.** Every new capability should be evaluated through the lens of "does this increase or decrease participant willingness to engage?"
- **Test with real thin-market dynamics.** The design should always be validated against scenarios where there are few participants, infrequent transactions, and high stakes per transaction — not against thick-market assumptions.

---

*This roadmap will be updated as implementation progresses and as the whitepaper framework evolves.*
