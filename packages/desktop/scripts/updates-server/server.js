import express from "express"
import cors from "cors"
import { readFileSync, existsSync, statSync, createReadStream } from "node:fs"
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

const BINARY_FILES = {
  "mac-x64": "novacode-desktop-mac-x64.dmg",
  "mac-arm64": "novacode-desktop-mac-arm64.dmg",
  "win-x64": "novacode-desktop-setup-win32-x64.exe",
  "win-arm64": "novacode-desktop-setup-win32-arm64.exe",
  "linux-x64": "novacode-desktop-linux-x64.AppImage",
  "linux-arm64": "novacode-desktop-linux-arm64.AppImage",
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

function sendFileWithCors(res, filePath, contentType) {
  if (!existsSync(filePath)) {
    return res.status(404).json({ error: "Not found", path: filePath })
  }

  const stats = statSync(filePath)
  res.setHeader("Content-Type", contentType)
  res.setHeader("Content-Length", stats.size)
  res.setHeader("Cache-Control", "public, max-age=60")
  res.setHeader("Access-Control-Allow-Origin", "*")
  res.setHeader("Access-Control-Allow-Methods", "GET, OPTIONS, HEAD")
  res.setHeader("Access-Control-Allow-Headers", "User-Agent, Range")
  res.setHeader("Accept-Ranges", "bytes")

  if (req.method === "OPTIONS") {
    return res.sendStatus(204)
  }

  createReadStream(filePath).pipe(res)
}

app.get("/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() })
})

app.get("/latest-mac.yml", (req, res) => {
  const platform = getPlatformFromUserAgent(req.headers["user-agent"])
  if (!platform) {
    return res.status(400).json({ error: "Cannot detect platform from User-Agent" })
  }

  const filename = PLATFORM_FILES[platform]
  const platformDir = platform.replace("-", "/")
  const filePath = path.join(ARTIFACTS_DIR, platformDir, filename)

  sendFileWithCors(res, filePath, "application/x-yaml")
})

app.get("/latest.yml", (req, res) => {
  const platform = getPlatformFromUserAgent(req.headers["user-agent"])
  if (!platform) {
    return res.status(400).json({ error: "Cannot detect platform from User-Agent" })
  }

  const filename = PLATFORM_FILES[platform]
  const platformDir = platform.replace("-", "/")
  const filePath = path.join(ARTIFACTS_DIR, platformDir, filename)

  sendFileWithCors(res, filePath, "application/x-yaml")
})

app.get("/latest-linux.yml", (req, res) => {
  const filePath = path.join(ARTIFACTS_DIR, "linux/x64", "latest-linux.yml")
  sendFileWithCors(res, filePath, "application/x-yaml")
})

app.get("/latest-linux-arm64.yml", (req, res) => {
  const filePath = path.join(ARTIFACTS_DIR, "linux/arm64", "latest-linux-arm64.yml")
  sendFileWithCors(res, filePath, "application/x-yaml")
})

app.get("/:platform/:filename", (req, res) => {
  const { platform, filename } = req.params
  const filePath = path.join(ARTIFACTS_DIR, platform, filename)
  const contentType = filename.endsWith(".yml") ? "application/x-yaml" : "application/octet-stream"
  sendFileWithCors(res, filePath, contentType)
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
