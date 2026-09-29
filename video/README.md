# Videos con Remotion

Proyecto para crear y editar videos automáticamente con código (React) usando [Remotion](https://www.remotion.dev).

## 1. Instalar en tu computadora (una sola vez)

### Node.js (obligatorio)
Descargá la versión **LTS** desde https://nodejs.org e instalala.
Comprobá en una terminal: `node -v` (debe ser 18 o superior).

### FFmpeg (recomendado)
Remotion 4 ya trae su propio FFmpeg interno para renderizar, pero conviene tener FFmpeg instalado
en el sistema para convertir, recortar o unir videos por fuera de Remotion.

- **Windows** (PowerShell): `winget install --id Gyan.FFmpeg -e`
- **macOS** (con Homebrew): `brew install ffmpeg`
- **Linux (Ubuntu/Debian)**: `sudo apt install ffmpeg`

Comprobá con: `ffmpeg -version` (en Windows, cerrá y abrí la terminal después de instalar).

## 2. Preparar el proyecto

```bash
git clone https://github.com/lucasolivera006-prog/prueba.git
cd prueba/video
npm install
```

La primera vez que renderices, Remotion descarga automáticamente un Chrome "headless" (~100 MB).

## 3. Uso

| Comando | Qué hace |
|---|---|
| `npm run studio` | Abre el editor visual en el navegador (http://localhost:3000) para ver y ajustar el video |
| `npm run render` | Genera `out/presentacion.mp4` (1920×1080, horizontal) |
| `npm run render:vertical` | Genera `out/presentacion-vertical.mp4` (1080×1920, para Reels/TikTok/Stories) |

### Cambiar textos sin tocar el código

```bash
npx remotion render Presentacion out/mi-video.mp4 --props='{"titulo":"Hola","subtitulo":"Mi texto","colorFondo":"#0f3d3e","colorTexto":"#ffffff"}'
```

En Windows (PowerShell), guardá los datos en un archivo `datos.json` y usá `--props=datos.json`.

## Estructura

- `src/Root.tsx` — lista de videos (composiciones), su tamaño, duración y FPS.
- `src/Presentacion.tsx` — el diseño y las animaciones del video de ejemplo.
- `public/` — poné acá imágenes, música o videos que quieras usar (con `staticFile("archivo.mp4")`).
- `out/` — videos generados (no se suben a git).

## Licencia de Remotion
Remotion es gratis para personas, y para empresas de hasta 3 empleados. Empresas más grandes necesitan
licencia paga: https://www.remotion.dev/license
