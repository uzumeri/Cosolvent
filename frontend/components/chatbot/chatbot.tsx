"use client";

import type React from "react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, MessageCircle, Send, User, X } from "lucide-react";
import ToolTip from "./toolTip";

import { askChatBot } from "@/lib/api/chatbot";
import { cn, scrollToRef } from "@/lib/utils";
import { useMutation } from "@tanstack/react-query";
import { v4 as uuidv4 } from "uuid";

type ChatMessage = {
	role: "user" | "assistant";
	text: string;
};

export default function Chatbot() {
	const [threadId] = useState<string>(() => uuidv4());
	const [isOpen, setIsOpen] = useState(false);
	const [showTooltip, setShowTooltip] = useState(true);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const lastMessageRef = useRef<HTMLDivElement>(null);

	const { mutate, isPending } = useMutation({
		mutationKey: ["chatbot"],
		mutationFn: askChatBot,
	});

	const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
	const [question, setQuestion] = useState<string>("");

	const handleChatToggle = () => {
		setIsOpen(!isOpen);
		setShowTooltip(false);
	};

	const handleQuessionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		setQuestion(() => e.target.value);
	};

	const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		if (question.trim()) {
			const newUserMessage: ChatMessage = {
				role: "user",
				text: question,
			};

			setQuestion("");

			setChatHistory((prev) => [...prev, newUserMessage]);

			mutate(
				{ threadId, question: newUserMessage.text },
				{
					onSuccess: (reponse) => {
						const newAssistantMessage: ChatMessage = {
							role: "assistant",
							text: reponse.data.aiResponse,
						};
						setChatHistory((prev) => [...prev, newAssistantMessage]);
					},
					onError: () => {
						const newAssistantMessage: ChatMessage = {
							role: "assistant",
							text: "Something went wrong, try again later",
						};
						setChatHistory((prev) => [...prev, newAssistantMessage]);
					},
				},
			);
		}
	};

	const scrollToNewMessage = () => {
		if (chatHistory.length > 0) {
			// If there's a new assistant message, scroll to show its beginning
			const lastMessage = chatHistory[chatHistory.length - 1];
			if (lastMessage.role === "assistant" && lastMessageRef.current) {
				scrollToRef(lastMessageRef, {
					behavior: "smooth",
					block: "start",
				});
			} else {
				// For user messages, scroll to bottom as usual
				scrollToRef(messagesEndRef);
			}
		}
	};

	// biome-ignore lint/correctness/useExhaustiveDependencies(chatHistory): suppress dependency chatHistory
	// biome-ignore lint/correctness/useExhaustiveDependencies(scrollToNewMessage): suppress dependency scrollToNewMessage
	useEffect(() => {
		scrollToNewMessage();
	}, [chatHistory]);

	return (
		<>
			{/* Animated Tooltip/indicator */}
			{showTooltip && !isOpen && (
				<ToolTip
					text="Need help?"
					showTooltip={showTooltip}
					setShowTooltip={setShowTooltip}
				/>
			)}
			{/* Floating Chat Button */}
			<Button
				onClick={handleChatToggle}
				className={cn(
					"fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg transition-all duration-300 z-50",
					"bg-black hover:bg-gray-800 text-white",
					isOpen && "rotate-180",
					showTooltip && !isOpen && "animate-pulse",
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
				<Card className="fixed bottom-24 right-6 w-80 h-96 shadow-2xl z-40 animate-in slide-in-from-bottom-2 duration-300 flex flex-col">
					<CardHeader className="pb-3 flex-shrink-0">
						<CardTitle className="flex items-center gap-2 text-lg">
							<Bot className="h-5 w-5 text-black" />
							Support AI
						</CardTitle>
					</CardHeader>

					<CardContent className="p-0 flex flex-col flex-1 min-h-0">
						{/* Messages Area */}
						<ScrollArea className="flex-1 px-4 min-h-0">
							<div className="space-y-4 py-4">
								{chatHistory.length === 0 && (
									<div className="text-center text-gray-500 text-sm py-8">
										<Bot className="h-8 w-8 mx-auto mb-2 text-gray-400" />
										<p>Hi! I&apos;m here to help.</p>
										<p>Ask me anything about the industry!</p>
									</div>
								)}

								{chatHistory.map((message, index) => (
									<div
										key={`${threadId + index}`}
										ref={
											index === chatHistory.length - 1 ? lastMessageRef : null
										}
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
											<div key={`${threadId + index}`}>{message.text}</div>
										</div>

										{message.role === "user" && (
											<div className="flex-shrink-0 w-6 h-6 rounded-full bg-black flex items-center justify-center">
												<User className="h-3 w-3 text-white" />
											</div>
										)}
									</div>
								))}

								{isPending && (
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
						<div className="border-t p-4 bg-white flex-shrink-0">
							<form onSubmit={onSubmit} className="flex gap-2">
								<Input
									value={question}
									onChange={handleQuessionChange}
									placeholder="Type your question here..."
									className="flex-1 text-sm border-gray-300 focus:border-black focus:ring-black"
									disabled={isPending}
								/>
								<Button
									type="submit"
									size="icon"
									disabled={isPending || !question.trim()}
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
