"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    Settings,
    Terminal,
    Users,
    Layers,
    LayoutDashboard,
    Plug
} from "lucide-react";

const navItems = [
    { name: "Dashboard", href: "/admin", icon: LayoutDashboard },
    { name: "Intelligence Slot", href: "/admin/config", icon: Settings },
    { name: "Market Physics", href: "/admin/market", icon: Layers },
    { name: "Prompt Studio", href: "/admin/prompts", icon: Terminal },
    { name: "MCP Slots", href: "/admin/mcp", icon: Plug },
];

export function AdminSidebar() {
    const pathname = usePathname();

    return (
        <div className="flex flex-col w-64 bg-slate-900 text-white min-h-screen border-r border-slate-800">
            <div className="p-6">
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                    Cosolvent Admin
                </h1>
                <p className="text-xs text-slate-400 mt-1">Thin Market Framework</p>
            </div>

            <nav className="flex-1 px-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 group",
                                isActive
                                    ? "bg-blue-600 text-white shadow-lg shadow-blue-900/20"
                                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                            )}
                        >
                            <item.icon className={cn(
                                "mr-3 h-5 w-5 transition-colors",
                                isActive ? "text-white" : "text-slate-500 group-hover:text-blue-400"
                            )} />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-slate-800">
                <div className="flex items-center p-2 rounded-lg bg-slate-800/50">
                    <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold">
                        AU
                    </div>
                    <div className="ml-3">
                        <p className="text-xs font-medium">Market Engineer</p>
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider">Admin Role</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
