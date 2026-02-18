"use client";

import { useEffect, useState } from "react";
import { adminApi, SystemPrompt } from "@/lib/api/admin";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2, Plus, Edit2, Trash2, Check, X } from "lucide-react";

export default function PromptsPage() {
    const [prompts, setPrompts] = useState<SystemPrompt[]>([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editValue, setEditValue] = useState("");

    useEffect(() => {
        loadPrompts();
    }, []);

    async function loadPrompts() {
        try {
            const res = await adminApi.listPrompts();
            setPrompts(res.data);
        } catch (err) {
            toast.error("Failed to load prompts");
        } finally {
            setLoading(false);
        }
    }

    async function handleSave(id: string) {
        try {
            await adminApi.updatePrompt(id, editValue);
            toast.success("Prompt updated");
            setEditingId(null);
            loadPrompts();
        } catch (err) {
            toast.error("Failed to update prompt");
        }
    }

    async function handleDelete(id: string) {
        if (!confirm("Are you sure?")) return;
        try {
            await adminApi.deletePrompt(id);
            toast.success("Prompt deleted");
            loadPrompts();
        } catch (err) {
            toast.error("Failed to delete prompt");
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
                    <h1 className="text-3xl font-bold">Prompt Studio</h1>
                    <p className="text-slate-400">The "AI Code" of your marketplace. Edit system behaviors.</p>
                </div>
                <Button className="bg-emerald-600 hover:bg-emerald-700">
                    <Plus className="mr-2 h-4 w-4" />
                    New Prompt
                </Button>
            </div>

            <div className="grid gap-6">
                {prompts.map((p) => (
                    <Card key={p.id} className="bg-slate-900 border-slate-800 transition-all hover:border-slate-700">
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <div className="space-y-1">
                                <CardTitle className="text-blue-400 font-mono text-sm">{p.id}</CardTitle>
                                <CardDescription className="text-[10px] text-slate-500">
                                    Last updated: {p.updated_at ? new Date(p.updated_at).toLocaleString() : 'Never'}
                                </CardDescription>
                            </div>
                            <div className="flex gap-2">
                                {editingId === p.id ? (
                                    <>
                                        <Button size="icon" variant="ghost" onClick={() => handleSave(p.id)} className="text-emerald-500">
                                            <Check className="h-4 w-4" />
                                        </Button>
                                        <Button size="icon" variant="ghost" onClick={() => setEditingId(null)} className="text-rose-500">
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </>
                                ) : (
                                    <>
                                        <Button size="icon" variant="ghost" onClick={() => {
                                            setEditingId(p.id);
                                            setEditValue(p.prompt);
                                        }} className="text-slate-400 hover:text-white">
                                            <Edit2 className="h-4 w-4" />
                                        </Button>
                                        <Button size="icon" variant="ghost" onClick={() => handleDelete(p.id)} className="text-slate-600 hover:text-rose-600">
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </>
                                )}
                            </div>
                        </CardHeader>
                        <CardContent>
                            {editingId === p.id ? (
                                <textarea
                                    value={editValue}
                                    onChange={(e) => setEditValue(e.target.value)}
                                    className="w-full h-48 bg-slate-950 border border-slate-700 rounded-md p-4 text-sm font-mono focus:ring-1 focus:ring-blue-500 outline-none"
                                />
                            ) : (
                                <div className="bg-slate-950/50 rounded-md p-4 text-xs text-slate-400 line-clamp-4 font-mono border border-slate-800/50">
                                    {p.prompt}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
