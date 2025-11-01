__include_modules__ = "SGP30"
__include_internal_modules__ = ""
__dependencies__ = "robtillaart/SGP30"


class SGP30Sensor:
    def __init__(self):
        """
        Create an instance of the SGP30 gas sensor class.

        You must call `.begin()` after instantiation to initialize I2C communication.
        """
        __use_as_is__ = False
        __class_actual_type__ = "SGP30"
        __translation__ = ""

    def begin(self) -> bool:
        """
        Initialize the sensor and begin I2C communication.

        Returns:
            bool: True if initialization succeeded, False otherwise.
        """
        __use_as_is__ = False
        __translation__ = "{self}.begin()"

    def is_connected(self) -> bool:
        """
        Check if the sensor is connected and responding over I2C.

        Returns:
            bool: True if the device is found on the I2C bus.
        """
        __use_as_is__ = False
        __translation__ = "{self}.isConnected()"

    def generic_reset(self) -> None:
        """
        Send a generic I2C reset command.

        ⚠️ WARNING: This may reset *all* I2C devices that respond to general reset!
        Use with caution in multi-device setups.
        """
        __use_as_is__ = False
        __translation__ = "{self}.GenericReset()"

    def get_id(self) -> bool:
        """
        Retrieve the sensor's internal ID into the _id[6] buffer.

        Returns:
            bool: True if ID was successfully read.
        """
        __use_as_is__ = False
        __translation__ = "{self}.getID()"

    def get_feature_set(self) -> int:
        """
        Get the firmware feature set version.

        Returns:
            int: Feature set code (e.g., 0x0020).
        """
        __use_as_is__ = False
        __translation__ = "{self}.getFeatureSet()"

    def measure_test(self) -> bool:
        """
        Run a sensor self-test (may be destructive depending on firmware).

        Returns:
            bool: True if test passed, False if failed.
        """
        __use_as_is__ = False
        __translation__ = "{self}.measureTest()"

    def last_measurement(self) -> int:
        """
        Get the timestamp (in ms) of the last successful measurement.

        Returns:
            int: Milliseconds since boot of last measurement.
        """
        __use_as_is__ = False
        __translation__ = "{self}.lastMeasurement()"

    def measure(self, all: bool = False) -> bool:
        """
        Perform a blocking measurement.

        Args:
            all (bool): If True, retrieves raw H2 and ethanol in addition to eCO2 and TVOC.

        Returns:
            bool: True if measurement succeeded.
        """
        __use_as_is__ = False
        __translation__ = "{self}.measure({all})"

    def request(self) -> None:
        """
        Request async measurement (non-blocking). Use `.read()` to get the result later.
        """
        __use_as_is__ = False
        __translation__ = "{self}.request()"

    def read(self) -> bool:
        """
        Read results from a previous async `.request()` call.

        Returns:
            bool: True if data was available and read successfully.
        """
        __use_as_is__ = False
        __translation__ = "{self}.read()"

    def request_raw(self) -> None:
        """
        Request a raw gas resistance measurement. Use `.read_raw()` to collect results.
        """
        __use_as_is__ = False
        __translation__ = "{self}.requestRaw()"

    def read_raw(self) -> bool:
        """
        Read raw values (H2 and ethanol) from the sensor after `.request_raw()`.

        Returns:
            bool: True if raw data was read successfully.
        """
        __use_as_is__ = False
        __translation__ = "{self}.readRaw()"

    def get_tvoc(self) -> int:
        """
        Get the Total Volatile Organic Compounds (TVOC) reading.

        Returns:
            int: TVOC value in parts per billion (ppb).
        """
        __use_as_is__ = False
        __translation__ = "{self}.getTVOC()"

    def get_co2(self) -> int:
        """
        Get the equivalent CO2 (eCO₂) concentration.

        Returns:
            int: CO2 concentration in parts per million (ppm).
        """
        __use_as_is__ = False
        __translation__ = "{self}.getCO2()"

    def get_h2_raw(self) -> int:
        """
        Get raw resistance signal related to hydrogen gas (H₂).

        Returns:
            int: Raw ADC units (hardware specific, not in ppm).
        """
        __use_as_is__ = False
        __translation__ = "{self}.getH2_raw()"

    def get_ethanol_raw(self) -> int:
        """
        Get raw resistance signal related to ethanol.

        Returns:
            int: Raw ADC units.
        """
        __use_as_is__ = False
        __translation__ = "{self}.getEthanol_raw()"

    def get_h2(self) -> float:
        """
        Estimate H₂ concentration from raw values using internal calibration.

        Returns:
            float: Hydrogen gas in PPM (experimental).
        """
        __use_as_is__ = False
        __translation__ = "{self}.getH2()"

    def get_ethanol(self) -> float:
        """
        Estimate ethanol concentration from raw values using internal calibration.

        Returns:
            float: Ethanol concentration in PPM (experimental).
        """
        __use_as_is__ = False
        __translation__ = "{self}.getEthanol()"

    def set_rel_humidity(self, temperature: float, rh: float) -> float:
        """
        Provide environmental compensation using temperature and relative humidity.

        Args:
            temperature (float): Temperature in °C.
            rh (float): Relative humidity (0–100%).

        Returns:
            float: Converted absolute humidity (g/m³).
        """
        __use_as_is__ = False
        __translation__ = "{self}.setRelHumidity({temperature}, {rh})"

    def set_abs_humidity(self, abs_humidity: float) -> None:
        """
        Set absolute humidity directly to improve sensor accuracy.

        Args:
            abs_humidity (float): Absolute humidity in grams per cubic meter (g/m³).
                                  Set to 0 to disable humidity compensation.
        """
        __use_as_is__ = False
        __translation__ = "{self}.setAbsHumidity({abs_humidity})"

    def set_baseline(self, co2: int, tvoc: int) -> None:
        """
        Set the known baseline values for eCO2 and TVOC.

        Args:
            co2 (int): Baseline CO2 in ppm.
            tvoc (int): Baseline TVOC in ppb.
        """
        __use_as_is__ = False
        __translation__ = "{self}.setBaseline({co2}, {tvoc})"

    def get_baseline(self, co2_ptr, tvoc_ptr) -> bool:
        """
        Retrieve the current baseline for eCO2 and TVOC.

        Args:
            co2_ptr: Pointer or container to receive CO2 baseline.
            tvoc_ptr: Pointer or container to receive TVOC baseline.

        Returns:
            bool: True if successful.
        """
        __use_as_is__ = False
        __translation__ = "{self}.getBaseline({co2_ptr}, {tvoc_ptr})"

    def set_tvoc_baseline(self, tvoc: int) -> None:
        """
        Set only the TVOC baseline value.

        Args:
            tvoc (int): TVOC baseline in ppb.
        """
        __use_as_is__ = False
        __translation__ = "{self}.setTVOCBaseline({tvoc})"

    def get_tvoc_baseline(self, tvoc_ptr) -> bool:
        """
        Retrieve only the TVOC baseline.

        Args:
            tvoc_ptr: Pointer or container to receive baseline.

        Returns:
            bool: True if successful.
        """
        __use_as_is__ = False
        __translation__ = "{self}.getTVOCBaseline({tvoc_ptr})"

    def set_sref_h2(self, s: int) -> None:
        """
        Set sensor reference value for H2 calibration (advanced use).

        Args:
            s (int): Raw average value from clean H₂ environment (e.g., 13119).
        """
        __use_as_is__ = False
        __translation__ = "{self}.setSrefH2({s})"

    def get_sref_h2(self) -> int:
        """
        Get current sensor reference value for H2 calibration.

        Returns:
            int: Raw reference value.
        """
        __use_as_is__ = False
        __translation__ = "{self}.getSrefH2()"

    def set_sref_ethanol(self, s: int) -> None:
        """
        Set sensor reference value for ethanol calibration (advanced use).

        Args:
            s (int): Raw average ethanol baseline value.
        """
        __use_as_is__ = False
        __translation__ = "{self}.setSrefEthanol({s})"

    def get_sref_ethanol(self) -> int:
        """
        Get current reference value used for ethanol baseline calibration.

        Returns:
            int: Raw baseline value.
        """
        __use_as_is__ = False
        __translation__ = "{self}.getSrefEthanol()"

    def last_error(self) -> int:
        """
        Return last I2C or CRC error code from any operation.

        Returns:
            int: 0 = OK, 0xFE = I2C error, 0xFF = CRC error.
        """
        __use_as_is__ = False
        __translation__ = "{self}.lastError()"
