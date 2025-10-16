# Arduino Wire Library Equivalents in Python

__include_modules__ = "Wire"
__dependencies__ = ""


def begin(address: int) -> None:
    """
    Initiates the Wire library and joins the I2C bus.

    Args:
        address (int, optional): If provided, sets the device as a slave with this address.

    Returns:
        None

    """
    __use_as_is__ = False
    __translation__ = "Wire.begin({0})"
    raise NotImplementedError()


def request_from(address: int, quantity: int, stop: int) -> int:
    """
    Requests bytes from a slave device.

    Args:
        address (int): The 7-bit address of the device to request bytes from.
        quantity (int): The number of bytes to request.
        stop (int): Whether to send a stop condition after the request (1 for true, 0 for false).

    Returns:
        int: The number of bytes returned from the slave device.

    """
    __use_as_is__ = False
    __translation__ = "Wire.requestFrom({0}, {1}, {2})"
    raise NotImplementedError()


def begin_transmission(address: int) -> None:
    """
    Begins a transmission to the I2C slave device with the given address.

    Args:
        address (int): The 7-bit address of the device to transmit to.

    Returns:
        None

    """
    __use_as_is__ = False
    __translation__ = "Wire.beginTransmission({0})"
    raise NotImplementedError()


def end_transmission(stop: bool) -> int:
    """
    Ends a transmission to a slave device and transmits the bytes that were queued.

    Args:
        stop (bool, optional): Whether to send a stop condition after the transmission (default is True).

    Returns:
        int: 0 if successful, or an error code.

    """
    __use_as_is__ = False
    __translation__ = "Wire.endTransmission({0})"
    raise NotImplementedError()


def write(data: int) -> int:
    """
    Sends data to a slave device.

    Args:
        data (int): The byte to send (0-255).

    Returns:
        int: The number of bytes written (should be 1 if successful).

    """
    __use_as_is__ = False
    __translation__ = "Wire.write({0})"
    raise NotImplementedError()


def read() -> int:
    """
    Reads a byte that was transmitted from a slave device to a master after a call to requestFrom().

    Returns:
        int: The next byte received.

    """
    __use_as_is__ = False
    __translation__ = "Wire.read()"
    raise NotImplementedError()


def available() -> int:
    """
    Returns the number of bytes available for retrieval with read().

    Returns:
        int: Number of bytes available to read.

    """
    __use_as_is__ = False
    __translation__ = "Wire.available()"
    raise NotImplementedError()


def on_receive(callback: callable) -> None:
    """
    Registers a function to be called when a slave device receives data from the master.

    Args:
        callback (Callable): A function that takes exactly **one integer argument** — the number of bytes received.
            Signature:
                def callback(num_bytes: int) -> None

            Example:
                def receive_handler(num_bytes):
                    # Read 'num_bytes' from Wire.read()
                    pass

    Returns:
        None

    """
    __use_as_is__ = False
    __translation__ = "Wire.onReceive({0})"
    raise NotImplementedError()


def on_request(callback: callable) -> None:
    """
    Registers a function to be called when a master requests data from this slave device.

    Args:
        callback (Callable): A function that takes **no arguments** and returns nothing.
            Signature:
                def callback() -> None

            Example:
                def request_handler():
                    # Use Wire.write(...) to send data
                    pass

    Returns:
        None

    """
    __use_as_is__ = False
    __translation__ = "Wire.onRequest({0})"
    raise NotImplementedError()
