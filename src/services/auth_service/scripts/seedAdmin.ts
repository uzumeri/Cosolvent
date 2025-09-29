import env from "@/config/env";
import readline from "node:readline";

const rl = readline.createInterface({
	input: process.stdin,
	output: process.stdout,
});

function prompt(question: string): Promise<string> {
	return new Promise((resolve) => {
		rl.question(question, (answer) => resolve(answer.trim()));
	});
}

async function seedAdmin() {

	const name = await prompt("📝 Enter admin name: ");
	const email = await prompt("📧 Enter admin email: ");
	const password = await prompt("🔐 Enter admin password: ");

	const adminData = {
		name,
		email,
		password,
		userType: "SERVICE_PROVIDER",
	};

	// Let the API decide if the user already exists

	//  Call API to create a user
	const res = await fetch(`${env.BASE_URL}/api/auth/sign-up/email`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(adminData),
	});

	if (!res.ok) {
		console.error("Failed to create user:", await res.text());
		process.exit(1);
	}

	const data = await res.json();
	console.log("User created:", data.user?.id ?? "unknown");
	console.log("NOTE: Granting admin role should be done via an admin endpoint or directly in Postgres.");

	console.log(`✅ Admin "${email}" created successfully.`);

	rl.close();
}

seedAdmin()
	.then(() => {
		console.log("✅ Seeder finished");
		process.exit(0);
	})
	.catch((err) => {
		console.error("Seeder error:", err);
		process.exit(1);
	});
