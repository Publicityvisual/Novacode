/**
 * Application-wide constants and configuration
 */
export const config = {
  // Base URL
  baseUrl: "https://novacode.ai",

  // GitHub
  github: {
    repoUrl: "https://github.com/anomalyco/novacode",
    starsFormatted: {
      compact: "208K",
      full: "208,000",
    },
  },

  // Social links
  social: {
    twitter: "https://x.com/novacode",
    discord: "https://discord.gg/novacode",
  },

  // Static stats (used on landing page)
  stats: {
    contributors: "950",
    commits: "13,000",
    monthlyUsers: "16M",
  },
} as const
