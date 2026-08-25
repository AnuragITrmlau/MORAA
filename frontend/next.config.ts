import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Explicitly set the project root so Turbopack resolves from the correct directory */
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
