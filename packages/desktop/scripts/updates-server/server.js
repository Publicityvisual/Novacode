import express from "express"
import cors from "cors"
import { readFileSync, existsSync, statSync, readdirSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const app = express()

app.use(cors())
app.use(express.json())

const ARTIFACTS_DIR = process.env.ARTIFACTS_DIR || path.join(__dirname, "artifacts")
const BASE_URL = process.env.BASE_URL || "https://novacode.dev/updates"

const PLATFORM_FILES = {
  "mac-x64": "latest-mac.yml",
  "mac-arm64": "latest-mac.yml",
  "win-x64": "latest.yml",
  "win-arm64": "latest.yml",
  "linux-x64": "latest-linux.yml",
  "linux-arm64": "latest-linux-arm64.yml",
}

function getPlatformFromUserAgent(userAgent) {
  if (!userAgent) return null
  const ua = userAgent.toLowerCase()
  if (ua.includes("macintosh") || ua.includes("mac os")) {
    if (ua.includes("arm") || ua.includes("aarch64")) return "mac-arm64"
    return "mac-x64"
  }
  if (ua.includes("windows")) {
    if (ua.includes("arm") || ua.includes("aarch64")) return "win-arm64"
    return "win-x64"
  }
  if (ua.includes("linux")) {
    if (ua.includes("aarch64") || ua.includes("arm64")) return "linux-arm64"
    return "linux-x64"
  }
  return null
}

app.get("/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() })
})

app.get("/:platform/:filename", (req, res) => {
  const { platform, filename } = req.params
  const filePath = path.join(ARTIFACTS_DIR, platform, filename)

  if (!existsSync(filePath)) {
    return res.status(404).json({ error: "Not found", path: filePath })
  }

  const stats = statSync(filePath)
  res.setHeader("Content-Type", "application/octet-stream")
  res.setHeader("Content-Length", stats.size)
  res.setHeader("Cache-Control", "public, max-age=300")
  res.setHeader("Access-Control-Allow-Origin", "*")
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS")
  res.setHeader("Access-Control-Allow-Headers", "User-Agent")

  if (req.method === "OPTIONS") {
    return res.sendStatus(204)
  }

  const stream = require("node:fs").createReadStream(filePath)
  stream.pipe(res)
})

app.get("/latest-mac.yml", (req, res) => {
  const platform = getPlatformFromUserAgent(req.headers["user-agent"])
  if (!platform) {
    return res.status(400).json({ error: "Cannot detect platform from User-Agent" })
  }

  const filename = PLATFORM_FILES[platform]
  const filePath = path.join(ARTIFACTS_DIR, platform.split("-")[0], platform.split("-")[1], filename)

  if (!existsSync(filePath)) {
    return res.status(404).json({ error: "Not found", path: filePath })
  }

  const content = readFileSync(filePath, "utf-8")
  res.setHeader("Content-Type", "application/x-yaml")
  res.setHeader("Cache-Control", "public, max-age=60")
  res.setHeader("Access-Control-Allow-Origin", "*")
  res.send(content)
})

app.get("/latest.yml", (req, res) => {
  const platform = getPlatformFromUserAgent(req.headers["user-agent"])
  if (!platform) {
    return res.status(400).json({ error: "Cannot detect platform from User-Agent" })
  }

  const filename = PLATFORM_FILES[platform]
  const filePath = path.join(ARTIFACTS_DIR, platform.split("-")[0], platform.split("-")[1], filename)

  if (!existsSync(filePath)) {
    return res.status(404).json({ error: "Not found", path: filePath })
  }

  const content = readFileSync(filePath, "utf-8")
  res.setHeader("Content-Type", "application/x-yaml")
  res.setHeader("Cache-Control", "public, max-age=60")
  res.setHeader("Access-Control-Allow-Origin", "*")
  res.send(content)
})

app.get("/latest-linux.yml", (req, res) => {
  const filePath = path.join(ARTIFACTS_DIR, "linux", "x64", "latest-linux.yml")
  if (!existsSync(filePath)) {
    return res.status(404).json({ error: "Not found" })
  }
  const content = readFileSync(filePath, "utf-8")
  res.setHeader("Content-Type", "application/x-yaml")
  res.setHeader("Cache-Control", "public, max-age=60")
  res.setHeader("Access-Control-Allow-Origin", "*")
  res.send(content)
})

app.get("/latest-linux-arm64.yml", (req, res) => {
  const filePath = path.join(ARTIFACTS_DIR, "linux", "arm64", "latest-linux-arm64.yml")
  if (!existsSync(filePath)) {
    return res.status(404).json({ error: "Not found" })
  }
  const content = readFileSync(filePath, "utf-8")
  res.setHeader("Content-Type", "application/x-yaml")
  res.setHeader("Cache-Control", "public, max-age=60")
  res.setHeader("Access-Control-Allow-Origin", "*")
  res.send(content)
})

app.get("/", (req, res) => {
  res.json({
    name: "NovaCode Updates Server",
    version: "1.0.0",
    endpoints: [
      "GET /latest-mac.yml",
      "GET /latest.yml",
      "GET /latest-linux.yml",
      "GET /latest-linux-arm64.yml",
      "GET /mac-arm64/novacode-desktop-mac-arm64.dmg",
      "GET /mac-x64/novacode-desktop-mac-x64.dmg",
      "GET /win-x64/novacode-desktop-setup-win32-x64.exe",
      "GET /win-arm64/novacode-desktop-setup-win32-arm64.exe",
      "GET /linux-x64/novacode-desktop-linux-x64.AppImage",
      "GET /linux-arm64/novacode-desktop-linux-arm64.AppImage",
    ],
  })
})

const PORT = process.env.PORT || 3000
app.listen(PORT, () => {
  console.log(`NovaCode updates server running on port ${PORT}`)
  console.log(`Artifacts directory: ${ARTIFACTS_DIR}`)
  console.log(`Base URL: ${BASE_URL}`)
})
