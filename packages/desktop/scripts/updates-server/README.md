# NovaCode Updates Server

Servidor de actualizaciones para NovaCode Desktop. Sirve los manifests `latest-*.yml` y binarios generados por electron-builder.

## Estructura de artifacts

```
artifacts/
├── mac-arm64/
│   ├── latest-mac.yml
│   └── novacode-desktop-mac-arm64.dmg
├── mac-x64/
│   ├── latest-mac.yml
│   └── novacode-desktop-mac-x64.dmg
├── win-x64/
│   ├── latest.yml
│   └── novacode-desktop-setup-win32-x64.exe
├── win-arm64/
│   ├── latest.yml
│   └── novacode-desktop-setup-win32-arm64.exe
├── linux-x64/
│   ├── latest-linux.yml
│   └── novacode-desktop-linux-x64.AppImage
└── linux-arm64/
    ├── latest-linux-arm64.yml
    └── novacode-desktop-linux-arm64.AppImage
```

## Cómo generar los artifacts

1. Build desde el paquete desktop:
```bash
cd packages/desktop
bun run build
bun run package:mac
bun run package:win
bun run package:linux
```

2. Deploy artifacts al server:
```bash
cd packages/desktop/scripts/updates-server
node deploy-artifacts.js
```

3. Commit y push de la carpeta `artifacts/` si usás Git-based deployment.

## Deployment

### Opción 1: Docker (recomendado)

```bash
cd packages/desktop/scripts/updates-server
docker compose up -d
```

### Opción 2: Railway / Render / Fly.io

- Conectá este directorio como repo
- Deploy automático
- Asegurate de que `artifacts/` esté incluido

### Opción 3: VPS propio

```bash
git clone https://github.com/Publicityvisual/Novacode.git
cd NovaCode/packages/desktop/scripts/updates-server
npm install
cp .env.example .env
npm start
```

### Opción 4: Cloudflare Pages + R2

1. Subir artifacts a Cloudflare R2
2. Usar Pages Functions para servir los manifests

## Variables de entorno

```env
PORT=3000
ARTIFACTS_DIR=./artifacts
BASE_URL=https://novacode.dev/updates
```

## CORS

El server responde con `Access-Control-Allow-Origin: *` para permitir que electron-updater consiga los manifests desde cualquier origen.

## Notas

- Los manifests `latest-*.yml` son generados por electron-builder durante el build
- El server detecta la plataforma desde el User-Agent y sirve el manifest correcto
- Los archivos se cachean por 60 segundos (manifest) o 300 segundos (binarios)
- El feed de actualizaciones está configurado en `packages/desktop/electron-builder.config.ts`
