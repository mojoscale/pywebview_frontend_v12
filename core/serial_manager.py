import serial
import serial.tools.list_ports
import time


def is_serial_port_connected():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        try:
            s = serial.Serial(port.device, 9600, timeout=1)
            s.close()
            return {"available": True, "port": port.device}
        except (serial.SerialException, OSError):
            continue
    return {"available": False}


def get_valid_serial_port(port_hint=None):
    """
    Try to find a serial port connected to a *real device*.
    Uses a hybrid detection strategy:
      1. If a hint is given, check if that port still exists and is usable.
      2. Prefer ports whose VID/PID or description match known USB-serial devices.
      3. If nothing matches, fall back to the first available port.

    Returns:
        str | None  ->  Path to serial port (e.g. 'COM3' or '/dev/ttyUSB0')
    """

    # --- Known vendor/product IDs for USB-to-serial adapters & dev boards ---
    KNOWN_USB_IDS = {
        ("10C4", "EA60"),  # Silicon Labs CP210x (ESP32, many dev boards)
        ("1A86", "7523"),  # CH340/CH341 (cheap ESP32 boards, Arduino clones)
        ("0403", "6001"),  # FTDI FT232
        ("2341", "0043"),  # Arduino Uno
        ("2341", "0001"),  # Arduino Duemilanove
        ("2E8A", "0005"),  # Raspberry Pi Pico
        ("10C4", "EA61"),  # CP2105
        # ⭐ ESP32-S3 Native USB (CDC, JTAG, etc)
        ("303A", "1001"),  # USB Serial/JTAG (Espressif)
        ("303A", "0002"),  # USB CDC
        ("303A", "4001"),  # USB JTAG only
    }

    # --- Common descriptive keywords to look for in device names ---
    KEYWORDS = [
        "cp210",
        "ch340",
        "ch341",
        "ftdi",
        "esp",
        "arduino",
        "usb-serial",
        "pico",
        "cdc",  # ⭐ for native USB
        "esp32-s3",  # Seeed board IDs
        "usb cdc",  # different OS variants
    ]

    # --- Helper to test if a port is openable ---
    def is_openable(device):
        try:
            s = serial.Serial(device, timeout=0.1)
            s.close()
            return True
        except Exception:
            return False

    ports = list(serial.tools.list_ports.comports())

    if not ports:
        print("🔴 No serial ports detected.")
        return None

    # 1️⃣ If a hint is provided, try it first
    if port_hint:
        for p in ports:
            if p.device == port_hint and is_openable(p.device):
                print(f"✅ Using hinted port: {p.device}")
                return p.device
        print(f"⚠️ Port hint {port_hint} not available, scanning others...")

        # 2️⃣ Look for known devices
        # 2️⃣ Look for known devices or Espressif native USB
        for p in ports:
            desc = (p.description or "").lower()
            hwid = (p.hwid or "").upper()

            # ⭐ Native ESP32-S3 (Seeed XIAO, ESP32-S3-DevKit, all S3 boards)
            if "VID_303A" in hwid or "VID:PID=303A" in hwid:
                print(f"⚡ ESP32-S3 Native USB detected on: {p.device}")
                return p.device

            # Old method for CP2102/CH340 etc. still works:
            vid = f"{p.vid:04X}" if p.vid is not None else None
            pid = f"{p.pid:04X}" if p.pid is not None else None

            if (vid, pid) in KNOWN_USB_IDS or any(k in desc for k in KEYWORDS):
                if is_openable(p.device):
                    print(
                        f"✅ Found likely device: {p.device} ({p.description}, VID={vid}, PID={pid})"
                    )
                    return p.device

            else:
                print(f"⚠️ Skipping {p.device}, not openable")

    # 3️⃣ Fallback to first openable port
    for p in ports:
        if is_openable(p.device):
            print(f"⚪ Falling back to first openable port: {p.device}")
            return p.device

    print("🔴 No usable serial ports found.")
    return None
