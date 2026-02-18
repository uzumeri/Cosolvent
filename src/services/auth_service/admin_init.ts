import { auth } from "./src/lib/auth";
import { Pool } from "pg";
import env from "./src/config/env";

async function run() {
    console.log("Checking tables...");
    const pool = new Pool({ connectionString: env.DATABASE_URL });
    
    // Better-auth doesn't have an easy auto-migrate in JS API sometimes
    // So we just try to sign up and see if it fails
    try {
        const user = await auth.api.signUpEmail({
            body: {
                email: "mustafa@deeperpoint.com",
                password: "Admin123!",
                name: "Mustafa Uzumeri",
                // @ts-ignore
                userType: "SERVICE_PROVIDER"
            }
        });
        console.log("User created:", user);
    } catch (e: any) {
        if (e.message?.includes("already exists")) {
            console.log("User already exists, continuing to role update.");
        } else {
            console.error("Signup failed:", e);
        }
    }
    
    console.log("Updating role to admin...");
    await pool.query('UPDATE "user" SET role = \'admin\' WHERE email = $1', ["mustafa@deeperpoint.com"]);
    console.log("✅ Admin role granted for mustafa@deeperpoint.com");
    await pool.end();
}

run().catch(console.error);
