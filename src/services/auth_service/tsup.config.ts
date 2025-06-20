import { defineConfig } from "tsup";

export default defineConfig({
	entry: ["src/server.ts"],
	outDir: "dist",
	format: ["esm"],
	target: "esnext",
	splitting: false, // disable code splitting for Node
	sourcemap: true,
	clean: true,
	dts: false,
	skipNodeModulesBundle: true,
	shims: false,
	esbuildOptions(options) {
		options.alias = {
			"@": "./src",
		};
	},
});
