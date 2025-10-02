/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      { source: '/', destination: '/fin-scenarios', permanent: false },
    ];
  },
};

module.exports = nextConfig;
