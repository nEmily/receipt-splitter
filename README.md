# Receipt Splitter

A kawaii offline-first PWA for snapping and queuing shared receipts. Works entirely on-device — the server is optional.

**[→ Open the app](https://nEmily.github.io/receipt-splitter/)**

No accounts. No cloud. No third parties. Just your phone and (optionally) your own computer.

---

## what it does

1. Open the PWA on your phone and add it to your home screen
2. Snap a photo of a receipt and jot a note ("mike and i split apps, i had 2 drinks")
3. Receipts are saved locally — they queue up until you're ready to review them
4. Optionally sync to a home server over your local network or Tailscale

The idea: capture receipts in the moment, sort out the math later. No pressure to split right now.

---

## using it

### just the app (no server needed)

Open [the PWA](https://nEmily.github.io/receipt-splitter/) in Safari on iOS or Chrome on Android. Add to home screen for the full standalone experience.

On first launch it asks for your name and an optional server URL. You can skip the server — receipts will queue locally and you can review them from the app.

### fork and deploy your own copy

The whole app is a single `index.html` file with no build step. To host your own copy:

1. Fork this repo
2. Go to **Settings → Pages → Source: Deploy from branch → Branch: main, folder /**
3. Your app lives at `https://<your-username>.github.io/receipt-splitter/`

### with a home server (optional)

If you want receipts to sync to a folder on your computer:

```powershell
cd server
pip install -r requirements.txt
python server.py
```

Set `RECEIPTS_DIR` to wherever you want receipts saved (defaults to `./receipts/`):

```powershell
$env:RECEIPTS_DIR = "C:\path\to\your\receipts"
python server.py
```

The server runs on port `5555` with a self-signed HTTPS cert. On first connection from your phone, accept the cert warning once — iOS requires HTTPS for camera access.

**Accessing from outside your home network:** [Tailscale](https://tailscale.com) works great. Enter your Tailscale IP as the server URL in the app (`https://100.x.x.x:5555`).

**Keeping it running on Windows:**

```powershell
$action  = New-ScheduledTaskAction -Execute "python" -Argument "server.py" -WorkingDirectory "C:\path\to\server"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ReceiptSplitter" -RunLevel Highest
```

---

## customizing with Claude

This app was built entirely with [Claude Code](https://claude.ai/code). If you want to adapt it — change the style, add features, modify how receipts are stored — open the project in Claude and describe what you want. The whole app is in three files (`index.html`, `sw.js`, `manifest.json`) so it's easy to work with.

Some ideas people might want to customize:
- Change where the server saves receipts (Dropbox, NAS, specific folder)
- Add a receipt review/ledger screen
- Change the aesthetic
- Add multi-person split math

---

## stack

- React 18 (no build step — Babel standalone)
- IndexedDB for offline queue
- Service worker for offline support + caching
- Flask + flask-cors for the optional upload server
- GitHub Pages for hosting

---

## privacy

Zero telemetry. Your name lives in `localStorage`. Receipt photos never leave your device unless you configure a server, and that server runs on your own hardware.

