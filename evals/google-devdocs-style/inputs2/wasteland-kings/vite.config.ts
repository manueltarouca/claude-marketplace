import { defineConfig } from "vite";

// Assets are fetched by the postinstall script into public/assets.
// Set SKIP_ASSETS=1 to skip that download.
export default defineConfig({
  server: { port: 5173 },
  build: { target: "es2022", outDir: "dist" },
});
