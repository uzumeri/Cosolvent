# Admin Interface Design: Thin Market Automation Framework

The Admin Interface (accessible at `/admin`) is the configuration cockpit for the marketplace. It allows a "Market Engineer" to define the market physics and AI interventions without redeploying code.

## 1. Intelligence Slot (AI Configuration)
*   **Purpose**: Define the LLM providers and models used for extraction, matching, and brokerage.
*   **Endpoint**: `GET /api/v1/config`, `PUT /api/v1/config`
*   **UI Elements**:
    *   API Key management for OpenRouter, Anthropic, etc.
    *   Dropdown to select "Default Model" for each service.
    *   Temperature/Token limits per service.

## 2. Market Definition (Dynamic Profiling)
*   **Purpose**: Define the structure of a "Participant" (e.g., Exporter, Developer, Property Owner).
*   **Endpoint**: `GET /api/v1/market`, `PUT /api/v1/market`
*   **UI Elements**:
    *   "Field Builder": Add/Remove fields (Text, Number, Date, List).
    *   Mark fields as "Extracted" (target for extraction prompt) or "Filterable".

## 3. Prompt Studio (The "Code" of AI)
*   **Purpose**: Version and edit the prompts that drive the market engineering.
*   **Endpoint**: `GET /api/v1/prompts`
*   **Key Prompts**:
    *   `matching_rationale`: Used to generate the "Why you were matched" text.
    *   `metadata_extraction`: Instructions for turning raw docs into the Market Participant schema.
    *   `broker_persona`: The voice of the asynchronous agent.

## 4. MCP Slots (Extensions)
*   **Purpose**: Connect the framework to external data sources and tools.
*   **Endpoint**: `GET /api/v1/mcp`
*   **Use Cases**:
    *   Connect to `Google Drive` for document ingestion.
    *   Connect to `GitHub` for developer profile analysis.
    *   Connect to `Slack` for agent notifications.

## 5. Implementation Roadmap (Frontend)
1.  **Dashboard**: Summary of Market Force scores (calculated via LLM analysis of participants).
2.  **Config Page**: Tabbed interface for Intelligence/Market/MCP settings.
3.  **Prompt Editor**: Markdown editor for prompt management.
