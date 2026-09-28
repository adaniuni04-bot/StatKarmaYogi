/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_URL ||
      (process.env.NODE_ENV === "development"
        ? "http://127.0.0.1:8000"
        : "");

    if (backendUrl) {
      return [
        {
          source: "/api/:path*",
          destination: `${backendUrl.replace(/\/+$/, "")}/api/:path*`,
        },
      ];
    }

    return [
      {
        source: "/api/:path*",
        destination: "/api/?__path=:path*",
      },
    ];
  },
};

module.exports = nextConfig;
