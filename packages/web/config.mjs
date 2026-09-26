const stage = process.env.SST_STAGE || "dev"

export default {
  url: stage === "production" ? "https://novacode.ai" : `https://${stage}.novacode.ai`,
  console: stage === "production" ? "https://novacode.ai/auth" : `https://${stage}.novacode.ai/auth`,
  email: "help@anoma.ly",
  socialCard: "https://social-cards.sst.dev",
  github: "https://github.com/anomalyco/novacode",
  discord: "https://novacode.ai/discord",
  headerLinks: [
    { name: "app.header.home", url: "/" },
    { name: "app.header.docs", url: "/v2/docs" },
  ],
}
