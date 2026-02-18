"use client";

import { useEffect, useState } from "react";
import { adminApi, SystemConfig } from "@/lib/api/admin";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Loader2, Save } from "lucide-react";

export default function ConfigPage() {
    const [config, setConfig] = useState<SystemConfig | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        loadConfig();
    }, []);

    async function loadConfig() {
        try {
            const res = await adminApi.getConfig();
            setConfig(res.data);
        } catch (err) {
            toast.error("Failed to load configuration");
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    async function handleSave() {
        if (!config) return;
        setSaving(true);
        try {
            await adminApi.updateConfig(config);
            toast.success("Configuration saved successfully");
        } catch (err) {
            toast.error("Failed to save configuration");
            console.error(err);
        } finally {
            setSaving(false);
        }
    }

    if (loading) {
        return (
            <div className="flex h-[400px] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Intelligence Slot</h1>
                    <p className="text-slate-400">Configure LLM providers and service defaults.</p>
                </div>
                <Button onClick={handleSave} disabled={saving} className="bg-blue-600 hover:bg-blue-700">
                    {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                    Save Changes
                </Button>
            </div>

            <div className="grid gap-6">
                <Card className="bg-slate-900 border-slate-800">
                    <CardHeader>
                        <CardTitle>API Clients</CardTitle>
                        <CardDescription className="text-slate-500">
                            Manage provider API keys and model endpoints.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {config && Object.entries(config.clients).map(([id, client]: [string, any]) => (
                            <div key={id} className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-4">
                                <div className="font-semibold text-blue-400 uppercase text-xs tracking-wider">{id}</div>
                                {Object.entries(client.providers).map(([pId, provider]: [string, any]) => (
                                    <div key={pId} className="grid grid-cols-2 gap-4 items-end">
                                        <div className="space-y-2">
                                            <Label className="text-xs text-slate-500">Model ID</Label>
                                            <Input
                                                value={provider.model}
                                                onChange={(e) => {
                                                    const newConfig = { ...config };
                                                    newConfig.clients[id].providers[pId].model = e.target.value;
                                                    setConfig(newConfig);
                                                }}
                                                placeholder="e.g. openai/gpt-5, anthropic/claude-3.5-sonnet"
                                                className="bg-slate-900 border-slate-700"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label className="text-xs text-slate-500">API Key Placeholder</Label>
                                            <Input
                                                type="password"
                                                value={provider.api_key}
                                                onChange={(e) => {
                                                    const newConfig = { ...config };
                                                    newConfig.clients[id].providers[pId].api_key = e.target.value;
                                                    setConfig(newConfig);
                                                }}
                                                className="bg-slate-900 border-slate-700"
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </CardContent>
                </Card>

                <Card className="bg-slate-900 border-slate-800">
                    <CardHeader>
                        <CardTitle>System Services</CardTitle>
                        <CardDescription className="text-slate-500">
                            Define which model and parameters each internal service uses.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {config && Object.entries(config.services).map(([id, service]: [string, any]) => (
                                <div key={id} className="p-4 rounded-lg bg-slate-950 border border-slate-800">
                                    <div className="flex justify-between items-center mb-4">
                                        <span className="font-bold text-slate-300 capitalize">{id.replace('_', ' ')}</span>
                                        <span className="text-[10px] bg-slate-800 px-2 py-1 rounded text-slate-500 uppercase">{service.provider}</span>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex justify-between text-xs">
                                            <span className="text-slate-500">Temperature</span>
                                            <span className="text-blue-400 font-mono">{service.options?.llm_params?.temperature ?? 'N/A'}</span>
                                        </div>
                                        <div className="flex justify-between text-xs">
                                            <span className="text-slate-500">Max Tokens</span>
                                            <span className="text-blue-400 font-mono">{service.options?.llm_params?.max_tokens ?? 'N/A'}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
