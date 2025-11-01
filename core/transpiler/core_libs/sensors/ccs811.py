"""
CCS811 Sensor Module
====================

This module provides a Python-style abstraction for the **Adafruit CCS811 Air Quality Sensor**, 
enabling seamless integration within the transpiler framework.

The CCS811 is a digital gas sensor capable of measuring **eCO₂ (equivalent CO₂)** and 
**TVOC (Total Volatile Organic Compounds)** concentrations. It communicates via I²C 
and benefits from environmental compensation inputs (humidity and temperature) for optimal accuracy.

Features
--------
- Initialize and configure the CCS811 sensor.
- Read eCO₂ (ppm) and TVOC (ppb) air quality measurements.
- Supply temperature and humidity compensation data.
- Retrieve thermistor-based temperature readings.
- Configure measurement frequency using drive modes.

Dependencies
------------
- Adafruit_CCS811
- Adafruit_I2CDevice
- adafruit/Adafruit BusIO (PlatformIO dependency)

Example
-------
```python
import sensors.ccs811 as ccs

sensor = ccs.CCS811Sensor()

def setup()->None:
    sensor.begin()

    while sensor.available():
        eco2 = sensor.get_eco2()
        tvoc = sensor.get_tvoc()


def loop()->None:
    pass 



```
"""


__include_modules__ = "Adafruit_CCS811,Adafruit_I2CDevice"
__include_internal_modules__ = ""
__dependencies__ = "adafruit/Adafruit BusIO"


class CCS811Sensor:
    """
    High-level Python wrapper for the Adafruit CCS811 gas sensor.

    Provides a convenient interface to initialize, read, and configure
    the CCS811 air quality sensor over I²C.
    """

    def __init__(self):
        """Initialize a CCS811 sensor instance."""
        __use_as_is__ = False
        __class_actual_type__ = "Adafruit_CCS811"
        __translation__ = ""

    def begin(self) -> bool:
        """Initialize communication with the CCS811 sensor via I²C."""
        __use_as_is__ = False
        __translation__ = "{self}.begin()"

    def available(self) -> bool:
        """Check whether new measurement data is available from the CCS811 sensor."""
        __use_as_is__ = False
        __translation__ = "{self}.available()"

    def read_data(self) -> bool:
        """Read the latest available data sample from the CCS811 sensor."""
        __use_as_is__ = False
        __translation__ = "{self}.readData()"

    def get_eco2(self) -> int:
        """Retrieve the equivalent CO₂ (eCO₂) reading in parts per million (ppm)."""
        __use_as_is__ = False
        __translation__ = "{self}.geteCO2()"

    def get_tvoc(self) -> int:
        """Retrieve the Total Volatile Organic Compounds (TVOC) reading in parts per billion (ppb)."""
        __use_as_is__ = False
        __translation__ = "{self}.getTVOC()"

    def set_environmental_data(self, humidity: float, temperature: float) -> None:
        """Provide humidity (%) and temperature (°C) data for compensation."""
        __use_as_is__ = False
        __translation__ = "{self}.setEnvironmentalData({humidity}, {temperature})"

    def calculate_temperature(self) -> float:
        """Calculate temperature using the onboard thermistor."""
        __use_as_is__ = False
        __translation__ = "{self}.calculateTemperature()"

    def set_drive_mode(self, mode: int) -> None:
        """Set the sensor’s drive mode (0–4) to define measurement frequency."""
        __use_as_is__ = False
        __translation__ = "{self}.setDriveMode({mode})"
