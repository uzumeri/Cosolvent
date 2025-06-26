import { Check } from "lucide-react";

interface StepperProps {
	currentStep: number;
	steps: string[];
}

export default function SignUpStepper({ currentStep, steps }: StepperProps) {
	return (
		<nav aria-label="Progress">
			<ol className="flex items-center">
				{steps.map((step, stepIdx) => (
					<li
						key={step}
						className={`relative ${stepIdx !== steps.length - 1 ? "pr-8 sm:pr-20" : ""}`}
					>
						{currentStep > stepIdx ? (
							// Completed Step
							<>
								<div
									className="absolute inset-0 flex items-center"
									aria-hidden="true"
								>
									<div className="h-0.5 w-full bg-primary" />
								</div>
								<div className="relative flex h-8 w-8 items-center justify-center bg-primary rounded-full text-primary-foreground">
									<Check className="h-5 w-5" aria-hidden="true" />
								</div>
							</>
						) : currentStep === stepIdx ? (
							// Current Step
							<>
								<div
									className="absolute inset-0 flex items-center"
									aria-hidden="true"
								>
									<div className="h-0.5 w-full bg-white/20" />
								</div>
								<div className="relative flex h-8 w-8 items-center justify-center bg-transparent border-2 border-primary rounded-full">
									<span
										className="h-2.5 w-2.5 bg-primary rounded-full"
										aria-hidden="true"
									/>
								</div>
							</>
						) : (
							// Upcoming Step
							<>
								<div
									className="absolute inset-0 flex items-center"
									aria-hidden="true"
								>
									<div className="h-0.5 w-full bg-white/20" />
								</div>
								<div className="relative flex h-8 w-8 items-center justify-center bg-transparent border-2 border-white/30 rounded-full" />
							</>
						)}
					</li>
				))}
			</ol>
		</nav>
	);
}
