import serial
import serial.tools.list_ports


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
    Try to confirm that a port is physically connected and openable.
    Returns a working port or None.
    """
    ports = list(serial.tools.list_ports.comports())

    # 1️⃣ If a hint is provided, check if it still exists
    if port_hint:
        for p in ports:
            if p.device == port_hint:
                try:
                    s = serial.Serial(p.device)
                    s.close()
                    return p.device
                except Exception:
                    break  # not accessible, fall through
        print(f"⚠️ Port {port_hint} no longer accessible, searching again...")

    # 2️⃣ Otherwise, find the first valid port
    for p in ports:
        try:
            s = serial.Serial(p.device)
            s.close()
            return p.device
        except Exception:
            continue

    return None
