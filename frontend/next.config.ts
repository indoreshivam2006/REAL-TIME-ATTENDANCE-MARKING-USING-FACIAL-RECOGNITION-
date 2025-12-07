import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output configuration for deployment
  output: 'standalone',
  
  // Image optimization
  images: {
    unoptimized: true, // Required for static export
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5000',
        pathname: '/**',
      },
    ],
  },
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  },
};

export default nextConfig;
