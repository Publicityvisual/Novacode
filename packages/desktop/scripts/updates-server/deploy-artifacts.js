#!/usr/bin/env node
import { execSync } from "node:child_process"
import { copyFileSync, existsSync, mkdirSync, readdirSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, "../../../..")
const DIST = path.join(ROOT, "packages/desktop/dist")
const ARTIFACTS = path.join(__dirname, "artifacts")

const PLATFORMS = [
  { name: "mac-arm64", manifest: "latest-mac.yml", binary: "novacode-desktop-mac-arm64.dmg" },
  { name: "mac-x64", manifest: "latest-mac.yml", binary: "novacode-desktop-mac-x64.dmg" },
  { name: "win-x64", manifest: "latest.yml", binary: "novacode-desktop-setup-win32-x64.exe" },
  { name: "win-arm64", manifest: "latest.yml", binary: "novacode-desktop-setup-win32-arm64.exe" },
  { name: "linux-x64", manifest: "latest-linux.yml", binary: "novacode-desktop-linux-x64.AppImage" },
  { name: "linux-arm64", manifest: "latest-linux-arm64.yml", binary: "novacode-desktop-linux-arm64.AppImage" },
]

function copyIfExists(src, dst) {
  if (existsSync(src)) {
    copyFileSync(src, dst)
    console.log(`✓ ${path.basename(src)}`)
  } else {
    console.log(`✗ Missing: ${src}`)
  }
}

function deploy() {
  console.log("Deploying NovaCode update artifacts...")

  for (const platform of PLATFORMS) {
    const platformDir = path.join(ARTIFACTS, platform.name)
    if (!existsSync(platformDir)) {
      mkdirSync(platformDir, { recursive: true })
    }

    const manifestSrc = path.join(DIST, platform.manifest)
    const manifestDst = path.join(platformDir, platform.manifest)

    const binarySrc = path.join(DIST, platform.binary)
    const binaryDst = path.join(platformDir, platform.binary)

    console.log(`\n${platform.name}:`)
    copyIfExists(manifestSrc, manifestDst)
    copyIfExists(binarySrc, binaryDst)
  }

  console.log("\n✓ Artifacts deployed to:", ARTIFACTS)
  console.log("\nNext steps:")
  console.log("1. Commit and push the artifacts/ directory")
  console.log("2. Deploy the updates server (see README.md)")
  console.log("3. Update DNS: novacode.dev/updates -> your server")
}

deploy()
