# WTFDIPI — Where The F*** Did I Put It

A self-hosted item-location tracker. Runs on a Raspberry Pi (or any machine with Python 3).

## Quick Start (Raspberry Pi)

### 1. Install uv (on the Pi)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### 2. Copy the project to your Pi

```bash
scp -r wtfdipi/ pi@raspberrypi.local:~/wtfdipi/
```

### 3. Run it

```bash
cd ~/wtfdipi
uv run python3 app.py
```

The app starts on **http://0.0.0.0:8000**, accessible from any device on your network at `http://<your-pi-ip>:8000`. Run `hostname -I` on the Pi to find its IP.

---

## Run on Boot (optional)

Create a systemd service so the app starts automatically on boot:

```bash
sudo nano /etc/systemd/system/wtfdipi.service
```

```ini
[Unit]
Description=WTFDIPI Item Tracker
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/wtfdipi
ExecStart=/home/pi/.local/bin/uv run python3 app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wtfdipi
sudo systemctl start wtfdipi
```

Useful commands:

```bash
sudo systemctl status wtfdipi   # check if running
sudo journalctl -u wtfdipi -f   # tail logs
sudo systemctl restart wtfdipi  # restart after updates
```

---

## Usage

1. **Locations** — add your storage spots
2. **Items** — add things you want to track
3. **Put** — record where you're placing something
4. **Find** — search for an item to see where it is

Data is stored in `wtfdipi.db` (SQLite). Back it up by copying that file.

---

## Production

For more robust deployments, run behind gunicorn:

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```
