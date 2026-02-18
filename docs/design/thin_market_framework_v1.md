# CosolventAI: Thin Market Automation Framework - Analysis & Design

## 1. Mapping: Existing Code vs. Thin Market Requirements

This section maps the current `CosolventAI` codebase to the "Market Physics" and "AI Interventions" defined in the Thin Markets Whitepaper (`tm-reference_CL4_V4.md`).

| Whitepaper Concept                            | CosolventAI Existing Component   | Status / Correspondence                                                                                      |
| :-------------------------------------------- | :------------------------------- | :----------------------------------------------------------------------------------------------------------- |
| **Market Physics: Information Density**       | `industry_context_service`       | **Partial.** Ingests docs/context. Strong foundation, but needs structured extraction of "dense" attributes. |
| **Market Physics: Opacity & Friction**        | `search_service` (Vector Search) | **Strong.** Uses `pgvector` for semantic matching. Reduces search friction.                                  |
| **Market Physics: Temporal Distance**         | *Missing*                        | No "Asynchronous Brokerage Agents" or "Time-Aware" constructs found.                                         |
| **AI Intervention: Semantic Matching**        | `search_service`                 | **Implemented.** Core matching logic exists.                                                                 |
| **AI Intervention: Trusted Intermediary**     | *Missing*                        | No "Confidential Vault" or "Double-Blind Matching" logic.                                                    |
| **AI Intervention: Input Friction Reduction** | `llm_orchestration_service`      | **Partial.** Has placeholders for `image_to_text`, `speech_to_text`. Needs real implementation.              |
| **Market Physics: Trust**                     | `profile_service`                | **Basic.** Simple profile CRUD. Missing "Trust Gradient" (verification, reputation, progressive disclosure). |

## 2. Gap Analysis: Critical Gaps for MVP

To operationalize Cosolvent as a **generic framework** (not just for Ag markets), the following gaps are critical:

1.  **Hard-Coded Domain Logic**:
    *   `profile_service` schemas are likely hard-coded to "Producers" (Agricultural).
    *   `industry_context_service` seems tuned to specific document types.
    *   **Fix**: Abstract "Producer" to "Participant" with dynamic schemas defined in Admin.

2.  **Missing "Time" & "Agent" Layer**:
    *   The "Asynchronous Brokerage Agent" (essential for bridging Temporal Distance) is missing.
    *   The system is currently "Request/Response" (User searches -> System returns). It needs to be "Agentic" (User posts intent -> Agent works over time).

3.  **Lack of Admin/Configuration Plane**:
    *   Configuration is in code/env/json files.
    *   No UI to "Swap LLM", "Edit Prompts", or "Connect Data Source".

4.  **No "Framework" Abstraction**:
    *   The system is a *single instance* of a market. It needs to be a *factory* for markets.

## 3. Design: Thin Market Automation Framework

### Core Philosophy
*   **Prompt-Driven Logic**: Logic for "Matching", "Extraction", and "Negotiation" moves from Code (Python/TS) to Prompts (Markdown/YAML) managed in Admin.
*   **MCP-First Integration**: External capabilities (LLMs, Data Sources, Tools) are treated as "Pluggable Resources" via MCP-like configuration.
*   **Slots Architecture**: The system defines "Functional Slots" that the Admin fills with specific implementations.

### 3.1 Admin Interface & MCP Slots

The Admin Interface will be the "Cockpit" for the Market Engineer. It allows configuration of the following **Slots**:

#### A. Intelligence Slot (The Brain)
*   **Definition**: Which LLM backs the system?
*   **Configuration**:
    *   Provider: `OpenRouter`, `Anthropic`, `OpenAI`, `Local`
    *   Model: `claude-3-5-sonnet`, `gpt-4o`
    *   **MCP Integration**: Use MCP to list available models and specific capabilities (e.g., specific context windows).

#### B. Context Slot (The Knowledge)
*   **Definition**: Where does the "Industry Context" come from?
*   **Configuration**:
    *   **Data Ingestion Sources**:
        *   `File Upload` (Native)
        *   `Google Drive` (via MCP)
        *   `Notion` (via MCP)
        *   `Web Scraper` (via MCP)
    *   **Vector Store**:
        *   `pgvector` (Internal)
        *   `Pinecone` (External)

#### C. Search Slot (The Matchmaker)
*   **Definition**: How do we match "Need" to "Have"?
*   **Configuration**:
    *   **Embedding Model**: `text-embedding-3`, `cohere-embed`
    *   **Matching Prompt**: *Critical*. The Admin writes the "Match Rationale Prompt".
        *   *Example*: "You are a matchmaker for high-end coffee. Compare these two profiles based on 'Flavor Profile' and 'Altitude'..."

#### D. Agent Slot (The Broker)
*   **Definition**: The "Personas" that act on behalf of users.
*   **Configuration**:
    *   **Broker Persona**: "You are a patient, detail-oriented broker..."
    *   **Negotiation Rules**: "Never offer below $X without approval."
    *   **Tools**: Give the agent access to "Search", "Schedule Meeting", "Send Quote".

### 3.2 System Architecture Changes

**1. `config_service` (New or Expanded Admin)**
*   Stores `FrameworkConfiguration` JSON in DB.
*   Replacing static `config.json` in `llm_orchestration_service`.

**2. `dynamic_profile_service`**
*   Replace hardcoded `Producer` schema with `DynamicSchema` (JSON Schema).
*   Admin defines "Profile Fields" (e.g., "Certification", "Crop Type" for Ag; "Tech Stack", "Rate" for Devs).

**3. `prompt_registry`**
*   Database table storing all system prompts.
*   Admin UI to edit/version prompts.
*   Service pulls prompts at runtime.

### 3.3 MVP Roadmap

1.  **Refactor Configuration**: Move `llm_orchestration_service/config.json` to a Database-backed Service.
2.  **Build Admin UI**:
    *   "AI Settings" page (Select LLM, Input Keys).
    *   "Prompt Studio" page (Edit System Prompts).
3.  **Implement MCP Client**:
    *   Allow the backend to "connect" to an MCP Server URL to discover tools (e.g., for Data Ingestion).
4.  **Abstract Profiling**:
    *   Allow Admin to define a "Profile Questionnaire" (Prompt-driven) instead of hardcoded fields.

## 4. Operationalizing Flexibility

To minimize hard-coding:
*   **Extraction**: Instead of writing regex/code for specific fields, the Admin writes an **Extraction Prompt**: "Extract 'Yield', 'Moisture', and 'Grade' from this document."
*   **Matching**: Instead of strict SQL filters, the Admin writes a **Ranking Prompt**: "Given User Request X and Candidates Y, Z... rank them by 'Compatibility'."

This shifts the "Business Logic" from *Code Deployment* to *Prompt Configuration*, enabling rapid adaptation to new Thin Markets.
