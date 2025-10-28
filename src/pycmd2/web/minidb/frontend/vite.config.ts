/// <reference types="vitest" />
import react from "@vitejs/plugin-react";
// @ts-ignore
import path from "path";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

// https://vitejs.dev/config/
// noinspection JSUnusedGlobalSymbols
export default defineConfig(({ mode }) => ({
  // @ts-ignore
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    // mode defines what ".env.{mode}" file to choose if exists
    env: loadEnv(mode, process.cwd(), ""),
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    coverage: {
      provider: "v8",
      reportsDirectory: "./html/coverage",
      include: ["src/**/*.{js,jsx,ts,tsx}"],
      reporter: ["html"],
    },
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
