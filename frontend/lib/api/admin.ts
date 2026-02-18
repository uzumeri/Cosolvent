import axios from './axios';

export interface SystemConfig {
    clients: Record<string, any>;
    services: Record<string, any>;
}

export interface SystemPrompt {
    id: string;
    prompt: string;
    created_at?: string;
    updated_at?: string;
}

export interface MarketField {
    name: string;
    type: string;
    description: string;
    required: boolean;
}

export interface MarketDefinition {
    name: string;
    description: string;
    participant_schema: MarketField[];
    matching_logic_prompt_id?: string;
    extraction_logic_prompt_id?: string;
}

export interface MCPServer {
    name: string;
    url: string;
    description?: string;
    enabled: boolean;
    capabilities: string[];
}

export interface MCPServerList {
    servers: MCPServer[];
}

export const adminApi = {
    // Configuration
    getConfig: () => axios.get<SystemConfig>('/admin/api/v1/config'),
    updateConfig: (config: SystemConfig) => axios.put<SystemConfig>('/admin/api/v1/config', config),
    patchConfig: (patch: Partial<SystemConfig>) => axios.patch<SystemConfig>('/admin/api/v1/config', patch),

    // Prompts
    listPrompts: () => axios.get<SystemPrompt[]>('/admin/api/v1/prompts'),
    getPrompt: (id: string) => axios.get<SystemPrompt>(`/admin/api/v1/prompts/${id}`),
    updatePrompt: (id: string, prompt: string) => axios.put<SystemPrompt>(`/admin/api/v1/prompts/${id}`, { prompt }),
    deletePrompt: (id: string) => axios.delete(`/admin/api/v1/prompts/${id}`),

    // Market
    getMarket: () => axios.get<MarketDefinition>('/admin/api/v1/market'),
    updateMarket: (market: MarketDefinition) => axios.put<MarketDefinition>('/admin/api/v1/market', market),

    // MCP
    listMCPServers: () => axios.get<MCPServerList>('/admin/api/v1/mcp'),
    updateMCPServers: (servers: MCPServerList) => axios.put<MCPServerList>('/admin/api/v1/mcp', servers),
};
