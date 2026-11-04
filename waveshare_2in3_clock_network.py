#!/usr/bin/env python3
"""Update a Waveshare 2.3" e-paper HAT with the current time and Wi‑Fi/IP details."""

import subprocess
import time
from PIL import Image, ImageDraw, ImageFont

# The Waveshare example repo installs this package:
#   git clone https://github.com/waveshareteam/e-Paper.git
#   cd e-Paper/RaspberryPi_JetsonNano/python
#   sudo python3 setup.py install
from waveshare_epd import epd2in13


DISPLAY_WIDTH = 212
DISPLAY_HEIGHT = 104


def get_network_info():
    """Return the Wi‑Fi SSID and current IP address for the Pi."""
    ssid = "No Wi‑Fi"
    ip = "No IP"

    try:
        ssid_raw = subprocess.check_output(["iwgetid", "-r"], stderr=subprocess.DEVNULL, text=True)
        ssid = ssid_raw.strip() or "No Wi‑Fi"
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    try:
        ip_raw = subprocess.check_output(["hostname", "-I"], text=True)
        parts = ip_raw.split()
        if parts:
            ip = parts[0]
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    return ssid, ip


def draw_screen(epd, ssid, ip):
    """Render the current time, SSID, and IP on the display."""
    image = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT), 255)  # white background
    draw = ImageDraw.Draw(image)

    # Fonts: fall back to default if the DejaVu font is unavailable
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]

    def load_font(size):
        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
        return ImageFont.load_default()

    time_font = load_font(22)
    label_font = load_font(16)

    now = time.strftime("%H:%M:%S")
    date_text = time.strftime("%a %d %b %Y")

    draw.text((5, 5), now, font=time_font, fill=0)
    draw.text((5, 35), date_text, font=label_font, fill=0)
    draw.text((5, 58), f"WiFi: {ssid}", font=label_font, fill=0)
    draw.text((5, 80), f"IP: {ip}", font=label_font, fill=0)

    epd.display(epd.getbuffer(image))


def main():
    epd = epd2in3.EPD()

    try:
        epd.init()
        epd.Clear()

        while True:
            ssid, ip = get_network_info()
            draw_screen(epd, ssid, ip)
            time.sleep(30)
    except KeyboardInterrupt:
        print("Stopping display updater")
    finally:
        try:
            epd.sleep()
        except Exception:
            pass


if __name__ == "__main__":
    main()
