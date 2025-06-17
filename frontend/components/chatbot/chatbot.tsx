"use client";

import type React from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn, scrollToBottom } from "@/lib/utils";
import { Bot, MessageCircle, Send, User, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";

type ChatMessage = {
	id: string;
	role: "user" | "assistant";
	text: string;
};

export default function Chatbot() {
	const [isOpen, setIsOpen] = useState(false);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
	const [question, setQuestion] = useState<string>("");
	const [isLoading, setIsLoading] = useState(false);

	const handleQuessionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setQuestion(() => e.target.value);
	};

	const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		if (question.trim()) {
			setIsLoading(true);
			const newMessage: ChatMessage = {
				id: uuidv4(),
				role: "user",
				text: question,
			};
			setChatHistory((prev) => [...prev, newMessage]);
		}
	};

	// biome-ignore lint/correctness/useExhaustiveDependencies(chatHistory): suppress dependency chatHistory
	useEffect(() => {
		scrollToBottom(messagesEndRef);
	}, [chatHistory]);

	return (
		<>
			{/* Floating Chat Button */}
			<Button
				onClick={() => setIsOpen(!isOpen)}
				className={cn(
					"fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg transition-all duration-300 z-50",
					"bg-black hover:bg-gray-800 text-white",
					isOpen && "rotate-180",
				)}
				size="icon"
			>
				{isOpen ? (
					<X className="h-6 w-6" />
				) : (
					<MessageCircle className="h-6 w-6" />
				)}
			</Button>

			{/* Chat Window */}
			{isOpen && (
				<Card className="fixed bottom-24 right-6 w-80 h-96 shadow-2xl z-40 animate-in slide-in-from-bottom-2 duration-300">
					<CardHeader className="pb-3">
						<CardTitle className="flex items-center gap-2 text-lg">
							<Bot className="h-5 w-5 text-black" />
							Support AI
						</CardTitle>
					</CardHeader>

					<CardContent className="p-0 flex flex-col h-full">
						{/* Messages Area */}
						<ScrollArea className="flex-1 px-4">
							<div className="space-y-4 pb-4">
								{chatHistory.length === 0 && (
									<div className="text-center text-gray-500 text-sm py-8">
										<Bot className="h-8 w-8 mx-auto mb-2 text-gray-400" />
										<p>Hi! I&apos;m your AgriSupport AI.</p>
										<p>Ask me about farming, crops, soil, or plant care!</p>
									</div>
								)}

								{chatHistory.map((message) => (
									<div
										key={message.id}
										className={cn(
											"flex gap-2 max-w-[85%] justify-end",
											message.role === "user" ? "ml-auto" : "mr-auto",
										)}
									>
										{message.role === "assistant" && (
											<div className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
												<Bot className="h-3 w-3 text-black" />
											</div>
										)}

										<div
											className={cn(
												"rounded-lg px-3 py-2 text-sm break-words",
												message.role === "user"
													? "bg-black text-white ml-2"
													: "bg-gray-100 text-gray-900",
											)}
										>
											<div key={`${message.id}`}>{message.text}</div>
										</div>

										{message.role === "user" && (
											<div className="flex-shrink-0 w-6 h-6 rounded-full bg-black flex items-center justify-center">
												<User className="h-3 w-3 text-white" />
											</div>
										)}
									</div>
								))}

								{isLoading && (
									<div className="flex gap-2 max-w-[85%] mr-auto">
										<div className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
											<Bot className="h-3 w-3 text-black" />
										</div>
										<div className="bg-gray-100 rounded-lg px-3 py-2 text-sm">
											<div className="flex space-x-1">
												<div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
												<div
													className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
													style={{ animationDelay: "0.1s" }}
												/>
												<div
													className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
													style={{ animationDelay: "0.2s" }}
												/>
											</div>
										</div>
									</div>
								)}

								<div ref={messagesEndRef} />
							</div>
						</ScrollArea>

						{/* Input Area */}
						<div className="border-t p-4 bg-white">
							<form onSubmit={onSubmit} className="flex gap-2">
								<Input
									value={question}
									onChange={handleQuessionChange}
									placeholder="Type your question here..."
									className="flex-1 text-sm border-gray-300 focus:border-black focus:ring-black"
									disabled={isLoading}
								/>
								<Button
									type="submit"
									size="icon"
									disabled={isLoading || !question.trim()}
									className="bg-black hover:bg-gray-800"
								>
									<Send className="h-4 w-4" />
								</Button>
							</form>
						</div>
					</CardContent>
				</Card>
			)}
		</>
	);
}
