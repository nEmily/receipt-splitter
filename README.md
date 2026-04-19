# receipt-splitter

A kawaii PWA for snapping and queuing shared receipts. Offline-first — receipts are saved locally and sync to your home server when you're back on wifi.

**[→ Open the app](https://nEmily.github.io/receipt-splitter/)**

## how it works

1. Open the PWA on your phone (add to home screen for the full experience)
2. First launch asks for your name + your Tailscale server URL
3. Snap a receipt → jot a quick note about who split what
4. It uploads directly to your home computer over Tailscale
5. Your `read_receipts.py` script picks it up on Sunday and does the math

No cloud, no accounts, no third parties — just your phone talking to your own computer.

## setup

### pwa (github pages)

The PWA lives at `https://nEmily.github.io/receipt-splitter/`. Open it in Safari, tap Share → Add to Home Screen for the full standalone experience.

On first launch it'll ask for:
- **Your name** — just for the greeting
- **Server URL** — your Tailscale server address, e.g. `https://100.x.x.x:5555` (you can skip this and add it later in settings)

All config stays in `localStorage` — nothing leaves your device.

### server (home computer)

```powershell
cd server
pip install -r requirements.txt
python server.py
```

The server runs on port `5555` with a self-signed HTTPS cert (required for camera access on iOS). On first connection from your phone, accept the cert warning once.

Set the `GDRIVE_ROOT` environment variable to your Google Drive path (e.g. `set GDRIVE_ROOT=C:\Users\you\My Drive`), or it defaults to `C:\Users\<your-username>\My Drive`.

### keeping it running

Use Windows Task Scheduler to run `server.py` at startup:

```powershell
$action  = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\server\server.py" -WorkingDirectory "C:\path\to\server"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ReceiptSplitter" -RunLevel Highest
```

## stack

- React 18 (no build step — Babel standalone for JSX)
- IndexedDB for offline queue
- Flask + flask-cors for the upload server
- Tailscale for secure remote access
- GitHub Pages for hosting

## privacy

Zero telemetry. Your name and server URL live in `localStorage` only. Receipt photos never leave your local network.
