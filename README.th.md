<p align="center">
  <a href="https://novacode.ai">
    <picture>
      <source srcset="packages/console/app/src/asset/logo-ornate-dark.svg" media="(prefers-color-scheme: dark)">
      <source srcset="packages/console/app/src/asset/logo-ornate-light.svg" media="(prefers-color-scheme: light)">
      <img src="packages/console/app/src/asset/logo-ornate-light.svg" alt="NovaCode logo">
    </picture>
  </a>
</p>
<p align="center">เอเจนต์การเขียนโค้ดด้วย AI แบบโอเพนซอร์ส</p>
<p align="center">
  <a href="https://novacode.ai/discord"><img alt="Discord" src="https://img.shields.io/discord/1391832426048651334?style=flat-square&label=discord" /></a>
  <a href="https://www.npmjs.com/package/novacode-ai"><img alt="npm" src="https://img.shields.io/npm/v/novacode-ai?style=flat-square" /></a>
  <a href="https://github.com/anomalyco/novacode/actions/workflows/publish.yml"><img alt="สถานะการสร้าง" src="https://img.shields.io/github/actions/workflow/status/anomalyco/novacode/publish.yml?style=flat-square&branch=dev" /></a>
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh.md">简体中文</a> |
  <a href="README.zht.md">繁體中文</a> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.de.md">Deutsch</a> |
  <a href="README.es.md">Español</a> |
  <a href="README.fr.md">Français</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.da.md">Dansk</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.ru.md">Русский</a> |
  <a href="README.bs.md">Bosanski</a> |
  <a href="README.ar.md">العربية</a> |
  <a href="README.no.md">Norsk</a> |
  <a href="README.br.md">Português (Brasil)</a> |
  <a href="README.th.md">ไทย</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a> |
  <a href="README.bn.md">বাংলা</a> |
  <a href="README.gr.md">Ελληνικά</a> |
  <a href="README.vi.md">Tiếng Việt</a>
</p>

[![NovaCode Terminal UI](packages/web/src/assets/lander/screenshot.png)](https://novacode.ai)

---

### การติดตั้ง

```bash
# YOLO
curl -fsSL https://novacode.ai/install | bash

# ตัวจัดการแพ็กเกจ
npm i -g novacode-ai@latest        # หรือ bun/pnpm/yarn
scoop install novacode             # Windows
choco install novacode             # Windows
brew install anomalyco/tap/novacode # macOS และ Linux (แนะนำ อัปเดตเสมอ)
brew install novacode              # macOS และ Linux (brew formula อย่างเป็นทางการ อัปเดตน้อยกว่า)
sudo pacman -S novacode            # Arch Linux (Stable)
paru -S novacode-bin               # Arch Linux (Latest from AUR)
mise use -g novacode               # ระบบปฏิบัติการใดก็ได้
nix run nixpkgs#novacode           # หรือ github:anomalyco/novacode สำหรับสาขาพัฒนาล่าสุด
```

> [!TIP]
> ลบเวอร์ชันที่เก่ากว่า 0.1.x ก่อนติดตั้ง

### แอปพลิเคชันเดสก์ท็อป (เบต้า)

NovaCode มีให้ใช้งานเป็นแอปพลิเคชันเดสก์ท็อป ดาวน์โหลดโดยตรงจาก [หน้ารุ่น](https://github.com/anomalyco/novacode/releases) หรือ [novacode.ai/download](https://novacode.ai/download)

| แพลตฟอร์ม             | ดาวน์โหลด                          |
| --------------------- | ---------------------------------- |
| macOS (Apple Silicon) | `novacode-desktop-mac-arm64.dmg`   |
| macOS (Intel)         | `novacode-desktop-mac-x64.dmg`     |
| Windows               | `novacode-desktop-windows-x64.exe` |
| Linux                 | `.deb`, `.rpm`, หรือ AppImage      |

```bash
# macOS (Homebrew)
brew install --cask novacode-desktop
# Windows (Scoop)
scoop bucket add extras; scoop install extras/novacode-desktop
```

#### ไดเรกทอรีการติดตั้ง

สคริปต์การติดตั้งจะใช้ลำดับความสำคัญตามเส้นทางการติดตั้ง:

1. `$OPENCODE_INSTALL_DIR` - ไดเรกทอรีการติดตั้งที่กำหนดเอง
2. `$XDG_BIN_DIR` - เส้นทางที่สอดคล้องกับ XDG Base Directory Specification
3. `$HOME/bin` - ไดเรกทอรีไบนารีผู้ใช้มาตรฐาน (หากมีอยู่หรือสามารถสร้างได้)
4. `$HOME/.novacode/bin` - ค่าสำรองเริ่มต้น

```bash
# ตัวอย่าง
OPENCODE_INSTALL_DIR=/usr/local/bin curl -fsSL https://novacode.ai/install | bash
XDG_BIN_DIR=$HOME/.local/bin curl -fsSL https://novacode.ai/install | bash
```

### เอเจนต์

NovaCode รวมเอเจนต์ในตัวสองตัวที่คุณสามารถสลับได้ด้วยปุ่ม `Tab`

- **build** - เอเจนต์เริ่มต้น มีสิทธิ์เข้าถึงแบบเต็มสำหรับงานพัฒนา
- **plan** - เอเจนต์อ่านอย่างเดียวสำหรับการวิเคราะห์และการสำรวจโค้ด
  - ปฏิเสธการแก้ไขไฟล์โดยค่าเริ่มต้น
  - ขอสิทธิ์ก่อนเรียกใช้คำสั่ง bash
  - เหมาะสำหรับสำรวจโค้ดเบสที่ไม่คุ้นเคยหรือวางแผนการเปลี่ยนแปลง

นอกจากนี้ยังมีเอเจนต์ย่อย **general** สำหรับการค้นหาที่ซับซ้อนและงานหลายขั้นตอน
ใช้ภายในและสามารถเรียกใช้ได้โดยใช้ `@general` ในข้อความ

เรียนรู้เพิ่มเติมเกี่ยวกับ [เอเจนต์](https://novacode.ai/docs/agents)

### เอกสารประกอบ

สำหรับข้อมูลเพิ่มเติมเกี่ยวกับวิธีกำหนดค่า NovaCode [**ไปที่เอกสารของเรา**](https://novacode.ai/docs)

### การมีส่วนร่วม

หากคุณสนใจที่จะมีส่วนร่วมใน NovaCode โปรดอ่าน [เอกสารการมีส่วนร่วม](./CONTRIBUTING.md) ก่อนส่ง Pull Request

### การสร้างบน NovaCode

หากคุณทำงานในโปรเจกต์ที่เกี่ยวข้องกับ NovaCode และใช้ "novacode" เป็นส่วนหนึ่งของชื่อ เช่น "novacode-dashboard" หรือ "novacode-mobile" โปรดเพิ่มหมายเหตุใน README ของคุณเพื่อชี้แจงว่าไม่ได้สร้างโดยทีม NovaCode และไม่ได้เกี่ยวข้องกับเราในทางใด

---

**ร่วมชุมชนของเรา** [Discord](https://discord.gg/novacode) | [X.com](https://x.com/novacode)
