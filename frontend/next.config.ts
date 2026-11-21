import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a small self-contained server bundle for the Docker image.
  output: "standalone",
};

export default nextConfig;
