"use client";

import { useEffect, useState } from "react";
import { adminApi, MarketDefinition } from "@/lib/api/admin";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Loader2, Plus, Trash2, Box } from "lucide-react";

export default function MarketPage() {
    const [market, setMarket] = useState<MarketDefinition | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadMarket();
    }, []);

    async function loadMarket() {
        try {
            const res = await adminApi.getMarket();
            setMarket(res.data);
        } catch (err) {
            toast.error("Failed to load market definition");
        } finally {
            setLoading(false);
        }
    }

    async function handleSave() {
        if (!market) return;
        try {
            await adminApi.updateMarket(market);
            toast.success("Market definition saved");
        } catch (err) {
            toast.error("Failed to save market definition");
        }
    }

    function addField() {
        if (!market) return;
        setMarket({
            ...market,
            participant_schema: [
                ...market.participant_schema,
                { name: "new_field", type: "string", description: "", required: false }
            ]
        });
    }

    function removeField(index: number) {
        if (!market) return;
        const newFields = [...market.participant_schema];
        newFields.splice(index, 1);
        setMarket({ ...market, participant_schema: newFields });
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
                    <h1 className="text-3xl font-bold">Market Physics</h1>
                    <p className="text-slate-400">Define the core dynamics and participant schemas of your marketplace.</p>
                </div>
                <Button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700">
                    Save Configuration
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1 space-y-6">
                    <Card className="bg-slate-900 border-slate-800">
                        <CardHeader>
                            <CardTitle>Market Info</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Market Name</Label>
                                <Input
                                    value={market?.name}
                                    onChange={(e) => setMarket(m => m ? { ...m, name: e.target.value } : null)}
                                    className="bg-slate-950 border-slate-800"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Description</Label>
                                <textarea
                                    value={market?.description}
                                    onChange={(e) => setMarket(m => m ? { ...m, description: e.target.value } : null)}
                                    className="w-full h-24 bg-slate-950 border border-slate-800 rounded-md p-2 text-sm text-slate-300"
                                />
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="lg:col-span-2 space-y-6">
                    <Card className="bg-slate-900 border-slate-800">
                        <CardHeader className="flex flex-row items-center justify-between">
                            <div>
                                <CardTitle>Participant Schema</CardTitle>
                                <CardDescription>Define what data constitutes a "Profile" in this market.</CardDescription>
                            </div>
                            <Button size="sm" variant="outline" onClick={addField} className="border-slate-700 text-slate-300">
                                <Plus className="h-4 w-4 mr-1" /> Add Field
                            </Button>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {market?.participant_schema.map((field, idx) => (
                                <div key={idx} className="flex gap-4 items-start p-4 rounded-lg bg-slate-950 border border-slate-800">
                                    <div className="bg-blue-900/20 p-2 rounded">
                                        <Box className="h-4 w-4 text-blue-400" />
                                    </div>
                                    <div className="flex-1 grid grid-cols-2 gap-4">
                                        <div className="space-y-1">
                                            <Label className="text-[10px] uppercase text-slate-500">Field Name</Label>
                                            <Input
                                                value={field.name}
                                                onChange={(e) => {
                                                    const newFields = [...market.participant_schema];
                                                    newFields[idx].name = e.target.value;
                                                    setMarket({ ...market, participant_schema: newFields });
                                                }}
                                                className="h-8 bg-slate-900 border-slate-800 text-sm"
                                            />
                                        </div>
                                        <div className="space-y-1">
                                            <Label className="text-[10px] uppercase text-slate-500">Type</Label>
                                            <select
                                                value={field.type}
                                                onChange={(e) => {
                                                    const newFields = [...market.participant_schema];
                                                    newFields[idx].type = e.target.value;
                                                    setMarket({ ...market, participant_schema: newFields });
                                                }}
                                                className="w-full h-8 bg-slate-900 border border-slate-800 rounded px-2 text-sm text-slate-300 outline-none"
                                            >
                                                <option value="string">String</option>
                                                <option value="number">Number</option>
                                                <option value="boolean">Boolean</option>
                                                <option value="array">Array</option>
                                            </select>
                                        </div>
                                    </div>
                                    <Button
                                        size="icon"
                                        variant="ghost"
                                        onClick={() => removeField(idx)}
                                        className="text-slate-600 hover:text-rose-500"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            ))}
                            {market?.participant_schema.length === 0 && (
                                <div className="text-center py-12 border-2 border-dashed border-slate-800 rounded-lg text-slate-500">
                                    No fields defined. Start by adding a field.
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
