# Cosolvent — Thin-Market Automation Framework (TMAF)

Cosolvent is an MIT-licensed, modular framework designed to automate **Thin Markets**—marketplaces characterized by informational opacity, high transaction costs, and scarce participation. 

Inspired by the **"Thin Markets: Market Physics and Engineering"** whitepaper, Cosolvent transforms static marketplace software into a dynamic, AI-orchestrated engine that can be tuned by a **Market Engineer** via a centralized control plane.

---

## 🚀 Key Framework Concepts

### 1. Functional Slots (The Architecture)
Cosolvent is built around "Slots" that separate the **Market Physics** (rules) from the **Intelligence** (logic) and **Context** (data).
- **Intelligence Slot**: Centralized LLM orchestration. Edit models, API keys, and parameters (temperature, max tokens) globally.
- **Context Slot (Authoritative Knowledge Base)**: Grounds AI agents in "curated truth." Ingests PDFs and whitepapers via a RAG pipeline to eliminate domain opacity.
- **Market Physics Slot**: Defines the "rules of the game" via dynamic participant schemas. Swap from "Coffee Exporters" to "DevOps Talent" by updating a JSON definition in the UI.
- **Agent Slot**: Asynchronous brokerage agents that handle persistence, negotiation, and long-running deal flows (v0.6).
- **Extension Slot (MCP)**: Pluggable Model Context Protocol servers that give the marketplace "hands" (e.g., real-time pricing tools, Drive ingestion).

### 2. Prompt-First Business Logic
Instead of hard-coded valuation or matching rules, Cosolvent uses a **System Prompt Registry**. You can edit the "Core Code" of your marketplace—extraction templates, match rationales, and agent personas—directly in the **Admin Cockpit**.

### 3. Preserving Heterogeneity
Unlike traditional marketplaces that force participants into narrow forms, Cosolvent uses **pgvector** and high-dimensional embeddings to match unique, complex profiles based on their true latent features.

---

## 🏗️ Microservices Overview (`src/services/`)

| Service               | Port   | Description                                                                                |
| :-------------------- | :----- | :----------------------------------------------------------------------------------------- |
| **Admin Service**     | `8003` | The framework's Control Plane. Manages Registry, Market Physics, and MCP configs.          |
| **LLM Orchestration** | `8000` | AI utility layer. Fetches prompts from the Registry to perform extraction and generation.  |
| **Profile Service**   | `5000` | Manages generic **Participants**. Uses a flexible JSONB schema to support any market type. |
| **Search Service**    | `5002` | **pgvector** search engine. Refactored for dynamic metadata filtering (zero schema-lock).  |
| **Industry Context**  | `8004` | RAG pipeline & MCP Discovery. Provides the "Authoritative Grounding" for the AI.           |
| **Asset Service**     | `5001` | Secure file ingestion (Images/PDFs) with S3 (MinIO) integration.                           |
| **Auth Service**      | `8020` | Unified authentication and RBAC session management.                                        |
| **Reverse Proxy**     | `80`   | Nginx-based unified API gateway with rate-limiting and security headers.                   |

---

## 📊 Infrastructure
- **Postgres + pgvector**: Unified storage for structured data and semantic embeddings.
- **Redis**: Caching and background job orchestration (BullMQ).
- **RabbitMQ**: Asynchronous message bus for cross-service events.
- **MinIO**: S3-compatible object storage for participant assets.

---

## 🛠️ Quickstart

### Prerequisites
- **Docker & Docker Compose**
- **Environment**: Copy `.env.example` to `.env` and provide your LLM API keys.

### Booting the Engine
```bash
docker compose up --build
```

### Accessing the Dashboard
- **Admin Cockpit**: `http://localhost:3000/admin`
  - *Note: Access requires the "admin" role. Use the built-in Auth Service to provision users.*
- **API Documentation**:
  - Admin (Control Plane): `http://localhost:8003/admin/docs`
  - LLM (Data Plane): `http://localhost:8000/docs`

---

## 🔌 Extending the Framework

Cosolvent is designed for **zero-downtime evolution**:
1. **New Market?** Create a new **Participant Schema** in the Market Physics tab.
2. **New Logic?** Update the relevant prompt in the **Prompt Studio**.
3. **New Data?** Connect an **MCP Server** (e.g., a GDrive folder of industry reports) in the MCP Slots tab.

---

## 🗺️ Roadmap
- [x] **v0.5 Framework Core**: Admin cockpit, Prompt Registry, Generic Participant abstraction.
- [ ] **v0.6 Agentic Brokerage**: Implementation of autonomous deal-making agents.
- [ ] **v0.7 Full MCP Orchestration**: Dynamic tool execution for market discovery.
- [ ] **v0.8 Synthetic Liquidity**: Integration with **ClientSynth** for market bootstrapping.

---

## 📜 License
MIT — See `LICENSE` for details.
