# WTFDIPI — Where The F*** Did I Put It

A self-hosted item-location tracker. Runs on a Raspberry Pi (or any machine with Python 3).

## Quick Start (Raspberry Pi)

### 1. Copy the project to your Pi

Copy the `wtfdipi/` folder to your Raspberry Pi (via USB, scp, git, etc.).

```bash
# Example: from your computer to the Pi over SSH
scp -r wtfdipi/ pi@raspberrypi.local:~/wtfdipi/
```

### 2. Install Flask

```bash
cd ~/wtfdipi
pip install -r requirements.txt
```

### 3. Run it

```bash
python3 app.py
```

The app starts on **http://0.0.0.0:5000**, so you can access it from:

- The Pi itself: `http://localhost:5000`
- Any device on your network: `http://<your-pi-ip>:5000`

To find your Pi's IP address, run `hostname -I` on the Pi.

---

## Run on Boot (optional)

To have WTFDIPI start automatically when your Pi boots, create a systemd service:

```bash
sudo nano /etc/systemd/system/wtfdipi.service
```

Paste this (adjust the paths/user if needed):

```ini
[Unit]
Description=WTFDIPI Item Tracker
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/wtfdipi
ExecStart=/usr/bin/python3 /home/pi/wtfdipi/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wtfdipi
sudo systemctl start wtfdipi
```

Check status anytime with:

```bash
sudo systemctl status wtfdipi
```

---

## Project Structure

```
wtfdipi/
├── app.py               # Flask server + REST API
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # Full frontend (single file)
└── wtfdipi.db           # SQLite database (created on first run)
```

---

## Usage

1. Open the app in a browser on any device on your network
2. Go to **📍 Locations** — add your storage spots
3. Go to **🏷 Items** — add things you want to track
4. Go to **📌 Put** — record where you're placing something
5. Go to **🔍 Find** — search for an item to see where it is

Data is stored in `wtfdipi.db` (SQLite). Back it up anytime by copying that file.

---

## Production Notes

The built-in Flask server works fine for personal/household use. If you want
something more robust, you can run it behind **gunicorn**:

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Update the `ExecStart` line in the systemd service accordingly.
