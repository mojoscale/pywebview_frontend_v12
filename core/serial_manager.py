import serial
import serial.tools.list_ports


def is_serial_port_connected():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "USB" in port.device or "COM" in port.device:
            print(f"[check] Serial port available: {port.device}")
            return {"available": True}
    return {"available": False}
