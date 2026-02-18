"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
	Activity,
	Cpu,
	Zap,
	Target,
	ArrowUpRight
} from "lucide-react";
import Link from "next/link";

const stats = [
	{ name: "Active Market Forces", value: "8/10", icon: Activity, trend: "+12%", color: "text-emerald-400" },
	{ name: "LLM Success Rate", value: "99.4%", icon: Cpu, trend: "+0.2%", color: "text-blue-400" },
	{ name: "Automation Velocity", value: "1.2s", icon: Zap, trend: "-150ms", color: "text-yellow-400" },
	{ name: "Matching precision", value: "94%", icon: Target, trend: "+4%", color: "text-purple-400" },
];

export default function AdminDashboard() {
	return (
		<div className="space-y-8">
			<div>
				<h1 className="text-3xl font-bold">Market Engineer Dashboard</h1>
				<p className="text-slate-400">Real-time health of your thin market framework.</p>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				{stats.map((stat) => (
					<Card key={stat.name} className="bg-slate-900 border-slate-800">
						<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
							<CardTitle className="text-sm font-medium text-slate-400">
								{stat.name}
							</CardTitle>
							<stat.icon className={`h-4 w-4 ${stat.color}`} />
						</CardHeader>
						<CardContent>
							<div className="text-2xl font-bold">{stat.value}</div>
							<p className="text-xs text-slate-500 mt-1">
								<span className="text-emerald-400 inline-flex items-center">
									<ArrowUpRight className="h-3 w-3 mr-1" /> {stat.trend}
								</span>{" "}
								vs last 7 days
							</p>
						</CardContent>
					</Card>
				))}
			</div>

			<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
				<Card className="bg-slate-900 border-slate-800">
					<CardHeader>
						<CardTitle>Recent Marketplace Activity</CardTitle>
					</CardHeader>
					<CardContent>
						<div className="space-y-4">
							{[1, 2, 3].map((i) => (
								<div key={i} className="flex items-start gap-4 p-3 rounded-lg bg-slate-950 border border-slate-800/50">
									<div className="h-2 w-2 mt-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
									<div>
										<p className="text-sm font-medium">New Participant Extracted</p>
										<p className="text-xs text-slate-500">LLM successfully parsed developer profile from PDF.</p>
										<p className="text-[10px] text-slate-600 mt-1 uppercase">2 minutes ago</p>
									</div>
								</div>
							))}
						</div>
					</CardContent>
				</Card>

				<Card className="bg-emerald-900/10 border-emerald-900/20">
					<CardHeader>
						<CardTitle className="text-emerald-400">Framework Recommendations</CardTitle>
					</CardHeader>
					<CardContent className="space-y-4">
						<div className="p-4 rounded-lg bg-emerald-950/20 border border-emerald-500/10">
							<h4 className="text-sm font-bold text-emerald-300">Increase Information Density</h4>
							<p className="text-xs text-emerald-500/80 mt-1">
								Detected high opacity in 'Product Grade' field. Consider updating the <strong>Extraction Prompt</strong> to capture more granular certification data.
							</p>
							<Link href="/admin/prompts" className="text-xs text-emerald-400 mt-3 inline-block hover:underline">
								Go to Prompt Studio &rarr;
							</Link>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
