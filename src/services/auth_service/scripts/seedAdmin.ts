import env from "@/config/env";
import { connectToDB } from "@/lib/db";
import { ObjectId } from "mongodb";
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
	const db = await connectToDB();

	const name = await prompt("📝 Enter admin name: ");
	const email = await prompt("📧 Enter admin email: ");
	const password = await prompt("🔐 Enter admin password: ");

	const adminData = {
		name,
		email,
		password,
		userType: "SERVICE_PROVIDER",
	};

	const userCollection = db.collection("user");

	const existingUser = await userCollection.findOne({ email });
	if (existingUser) {
		console.log(`⚠️  User with email "${email}" already exists.`);
		rl.close();
		process.exit(1);
	}

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
	const userId = new ObjectId(data.user.id);

	try {
		await userCollection.updateOne(
			{ _id: userId },
			{ $set: { role: "admin", userType: "admin", emailVerified: true } },
		);
	} catch (error) {
		console.error("Failed to update user:", error);
		process.exit(1);
	}

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
