"""
FastAccelStepper Python Wrapper for ESP32 and Arduino boards.

A high-speed stepper motor control library providing acceleration/deceleration,
non-blocking movement, and multi-motor support. This wrapper provides a Pythonic
interface to the underlying C++ FastAccelStepper library.

Classes:
    FastAccelStepperEngine: Factory and resource manager for stepper motors
    FastAccelStepper: Individual stepper motor controller

Example:
    Basic usage with blocking movement:
    
    >>> engine = FastAccelStepperEngine()
    >>> engine.init()
    >>> stepper = engine.stepper_connect_to_pin(9)
    >>> if stepper:
    ...     stepper.set_direction_pin(5)
    ...     stepper.set_enable_pin(6)
    ...     stepper.set_speed_hz(500)
    ...     stepper.set_acceleration(100)
    ...     stepper.move_to(1000, True)  # Blocking move

    Non-blocking movement with status polling:
    
    >>> stepper.move_to(5000)  # Start non-blocking move
    >>> while stepper.is_running():
    ...     # Do other work
    ...     pass
"""

__include_modules__ = "FastAccelStepper"
__dependencies__ = "gin66/FastAccelStepper"
__include_internal_modules__ = "helpers/actuators/FastAccelStepperHelper"


class FastAccelStepperEngine:
    """
    Factory and resource manager for stepper motors.

    The engine manages hardware resources (timers, modules, interrupts) and
    coordinates multiple stepper motors. It handles platform-specific complexity
    and ensures efficient resource allocation.

    On ESP32: Manages MCPWM, RMT, and pulse counter modules
    On AVR: Manages timer allocation
    On Pico: Manages PIO state machines

    Attributes:
        None (engine manages resources internally)
    """

    def __init__(self):
        """
        Initialize the FastAccelStepperEngine factory.

        Creates an engine instance. Must call init() before connecting steppers.

        Returns:
            FastAccelStepperEngine: New engine instance
        """
        __class_actual_type__ = "FastAccelStepperEngine"
        __translation__ = ""
        pass

    def init(self) -> None:
        """
        Initialize the stepper engine and allocate hardware resources.

        Sets up interrupt handlers, timers, and tasks needed for stepper control.
        Must be called in setup() before connecting any steppers.

        On ESP32, the stepper task runs on the default core. This method is
        blocking only for setup duration.

        Args:
            None

        Returns:
            None

        Raises:
            RuntimeError: If hardware resources are unavailable

        Example:
            >>> engine = FastAccelStepperEngine()
            >>> engine.init()
        """
        __translation__ = "{0}.init()"
        pass

    def stepper_connect_to_pin(self, step_pin: int) -> FastAccelStepper:
        """
        Create and connect a new stepper to a step pin.

        Allocates hardware resources (timer/module) and creates a FastAccelStepper
        instance for control. Returns None if the pin cannot be used or no
        resources are available.

        Step pin restrictions vary by platform:
        - AVR Nano/Uno: Pins 9, 10
        - AVR Mega2560: Pins 6, 7, 8
        - ESP32: Any GPIO pin
        - Pico: Any GPIO up to 31

        Args:
            step_pin (int): GPIO pin number for step signal

        Returns:
            FastAccelStepper: New stepper instance, or None if allocation failed

        Example:
            >>> stepper = engine.stepper_connect_to_pin(9)
            >>> if stepper:
            ...     stepper.set_direction_pin(5)
        """
        __translation__ = "{0}.stepperConnectToPin({1})"
        pass


class FastAccelStepper:
    """
    Individual stepper motor controller with acceleration support.

    Manages a single stepper motor including speed, acceleration, and position.
    The controller is fully non-blocking - no periodic function calls required
    in the main loop. All timing is interrupt-driven.

    Attributes:
        None (state managed internally by C++ driver)

    Note:
        Do not instantiate directly. Use FastAccelStepperEngine.stepper_connect_to_pin()
    """

    # ========== PIN CONFIGURATION ==========

    def __init__(self):
        __pass_as__ = "pointer"

    def set_direction_pin(self, pin: int) -> None:
        """
        Configure the direction control pin.

        Sets the GPIO pin used to control stepper direction. Direction signal
        transitions should allow adequate settling time (see set_direction_delay).
        By default, HIGH counts up and LOW counts down.

        Args:
            pin (int): GPIO pin number for direction control

        Returns:
            None

        Example:
            >>> stepper.set_direction_pin(5)
        """
        __translation__ = "{0}->setDirectionPin({1})"

    def get_direction_pin(self) -> int:
        """
        Get the configured direction pin.

        Returns the GPIO pin number that was set for direction control.

        Args:
            None

        Returns:
            int: GPIO pin number for direction control

        Example:
            >>> pin = stepper.get_direction_pin()
        """
        __translation__ = "{0}->getDirectionPin()"

    def direction_pin_high_counts_up(self) -> bool:
        """
        Get the direction pin polarity setting.

        Returns whether HIGH on the direction pin counts up (True) or down (False).

        Args:
            None

        Returns:
            bool: True if HIGH counts up, False if HIGH counts down

        Example:
            >>> if stepper.direction_pin_high_counts_up():
            ...     print("HIGH = forward")
        """
        __translation__ = "{0}->directionPinHighCountsUp()"

    def set_enable_pin(self, pin: int, low_active: bool = True) -> None:
        """
        Configure the motor enable pin.

        Sets the GPIO pin used to enable/disable the stepper driver. By default,
        LOW activates the driver.

        Args:
            pin (int): GPIO pin number for enable control
            low_active (bool): If True (default), LOW enables driver.
                              If False, HIGH enables driver.

        Returns:
            None

        Example:
            >>> stepper.set_enable_pin(6)
            >>> stepper.set_enable_pin(6, False)  # HIGH enables
        """
        __translation__ = "{0}->setEnablePin({1}, {2})"

    def get_enable_pin_low_active(self) -> int:
        """
        Get the low-active enable pin number.

        Returns the GPIO pin configured for low-active enable (if any).

        Args:
            None

        Returns:
            int: GPIO pin number or 0 if not configured

        Example:
            >>> pin = stepper.get_enable_pin_low_active()
        """
        __translation__ = "{0}->getEnablePinLowActive()"

    def get_enable_pin_high_active(self) -> int:
        """
        Get the high-active enable pin number.

        Returns the GPIO pin configured for high-active enable (if any).

        Args:
            None

        Returns:
            int: GPIO pin number or 0 if not configured

        Example:
            >>> pin = stepper.get_enable_pin_high_active()
        """
        __translation__ = "{0}->getEnablePinHighActive()"

    def set_auto_enable(self, enable: bool) -> None:
        """
        Enable automatic motor enable/disable with movement.

        When enabled, the motor is automatically powered on when movement starts
        and powers off when movement completes. Reduces power dissipation and
        heat generation during idle periods.

        Args:
            enable (bool): True to enable auto enable/disable, False for manual control

        Returns:
            None

        Example:
            >>> stepper.set_auto_enable(True)
        """
        __translation__ = "{0}->setAutoEnable({1})"

    def set_delay_to_enable(self, delay_us: int) -> int:
        """
        Set delay between enable and first step.

        Specifies the time the motor driver has to stabilize after being enabled
        before the first step pulse is issued.

        Args:
            delay_us (int): Delay in microseconds (max ~120ms on ESP32)

        Returns:
            int: DelayResultCode (0 = DELAY_OK, -1 = out of range)

        Example:
            >>> stepper.set_delay_to_enable(500)  # 500 microseconds
        """
        __translation__ = "{0}->setDelayToEnable({1})"

    def set_delay_to_disable(self, delay_ms: int) -> None:
        """
        Set delay between last step and disable.

        Specifies the time to wait after the last step before disabling the motor.

        Args:
            delay_ms (int): Delay in milliseconds

        Returns:
            None

        Example:
            >>> stepper.set_delay_to_disable(5)  # 5 milliseconds
        """
        __translation__ = "{0}->setDelayToDisable({1})"

    # ========== SPEED CONTROL ==========

    def set_speed_hz(self, speed_hz: int) -> int:
        """
        Set stepper speed in steps per second.

        Sets the target speed for movement. Speed is applied to the next
        move/moveTo/runForward/runBackward call. Changes to a running motor
        require calling move() again to take effect.

        Valid range: ~244 Hz (minimum) to hardware maximum (~92kHz on ESP32).
        Hardware maximum depends on CPU frequency and driver module.

        Args:
            speed_hz (int): Target speed in steps per second (Hz)

        Returns:
            int: 0 on success, -1 if speed exceeds hardware limits

        Example:
            >>> result = stepper.set_speed_hz(500)
            >>> if result == 0:
            ...     print("Speed set successfully")
        """
        __translation__ = "{0}->setSpeedInHz({1})"

    def set_speed_us(self, step_us: int) -> int:
        """
        Set stepper speed in microseconds per step.

        Alternative to set_speed_hz() using microsecond resolution.
        Useful for very precise speed control or when working with timing constants.

        Args:
            step_us (int): Minimum time between steps in microseconds

        Returns:
            int: 0 on success, -1 if speed is invalid

        Example:
            >>> stepper.set_speed_us(2000)  # 2ms per step = 500 Hz
        """
        __translation__ = "{0}->setSpeedInUs({1})"

    def set_speed_ticks(self, step_ticks: int) -> int:
        """
        Set stepper speed in CPU ticks per step.

        Low-level API for experienced users. Ticks depend on CPU frequency.
        At 16MHz: 1 tick = 62.5ns, at 240MHz (ESP32): 1 tick = 4.17ns.

        Args:
            step_ticks (int): Minimum ticks between steps

        Returns:
            int: 0 on success, -1 if speed is invalid

        Example:
            >>> stepper.set_speed_ticks(3200)
        """
        __translation__ = "{0}->setSpeedInTicks({1})"

    def set_speed_millihz(self, speed_millihz: int) -> int:
        """
        Set stepper speed in millihertz (steps per 1000 seconds).

        For very slow speeds. Useful for applications requiring sub-Hz control
        like automated plant waterers or time-lapse mechanisms.

        Args:
            speed_millihz (int): Speed in millihertz

        Returns:
            int: 0 on success, -1 if speed is invalid

        Example:
            >>> stepper.set_speed_millihz(100)  # 0.1 steps per second
        """
        __translation__ = "{0}->setSpeedInMilliHz({1})"

    def get_speed_us(self) -> int:
        """
        Get configured speed in microseconds per step.

        Returns the speed that was set, not accounting for acceleration.

        Args:
            None

        Returns:
            int: Speed in microseconds per step

        Example:
            >>> speed_us = stepper.get_speed_us()
        """
        __translation__ = "{0}->getSpeedInUs()"

    def get_speed_ticks(self) -> int:
        """
        Get configured speed in CPU ticks per step.

        Returns the speed that was set in ticks.

        Args:
            None

        Returns:
            int: Speed in ticks per step

        Example:
            >>> speed_ticks = stepper.get_speed_ticks()
        """
        __translation__ = "{0}->getSpeedInTicks()"

    def get_speed_millihz(self) -> int:
        """
        Get configured speed in millihertz.

        Returns the speed that was set in millihertz.

        Args:
            None

        Returns:
            int: Speed in millihertz

        Example:
            >>> speed_mhz = stepper.get_speed_millihz()
        """
        __translation__ = "{0}->getSpeedInMilliHz()"

    def get_current_speed_us(self) -> int:
        """
        Get actual current speed in microseconds per step.

        Returns the actual speed being executed, accounting for acceleration.
        During ramp-up/down, this changes over time. Returns negative during
        backward movement.

        Args:
            None

        Returns:
            int: Current speed in microseconds per step (negative = backward)

        Example:
            >>> current_speed = stepper.get_current_speed_us()
        """
        __translation__ = "{0}->getCurrentSpeedInUs()"

    def get_current_speed_millihz(self) -> int:
        """
        Get actual current speed in millihertz.

        Returns the actual speed being executed, accounting for acceleration.

        Args:
            None

        Returns:
            int: Current speed in millihertz (negative = backward)

        Example:
            >>> current_speed = stepper.get_current_speed_millihz()
        """
        __translation__ = "{0}->getCurrentSpeedInMilliHz()"

    def get_max_speed_hz(self) -> int:
        """
        Get hardware maximum speed in Hz.

        Returns the maximum achievable speed on this hardware.

        Args:
            None

        Returns:
            int: Maximum speed in Hz

        Example:
            >>> max_hz = stepper.get_max_speed_hz()
        """
        __translation__ = "{0}->getMaxSpeedInHz()"

    def get_max_speed_us(self) -> int:
        """
        Get hardware maximum speed in microseconds per step.

        Returns the maximum achievable speed on this hardware.

        Args:
            None

        Returns:
            int: Minimum microseconds per step

        Example:
            >>> max_speed_us = stepper.get_max_speed_us()
        """
        __translation__ = "{0}->getMaxSpeedInUs()"

    def get_max_speed_ticks(self) -> int:
        """
        Get hardware maximum speed in CPU ticks per step.

        Returns the maximum achievable speed on this hardware.

        Args:
            None

        Returns:
            int: Minimum ticks per step

        Example:
            >>> max_speed_ticks = stepper.get_max_speed_ticks()
        """
        __translation__ = "{0}->getMaxSpeedInTicks()"

    def get_max_speed_millihz(self) -> int:
        """
        Get hardware maximum speed in millihertz.

        Returns the maximum achievable speed on this hardware.

        Args:
            None

        Returns:
            int: Maximum speed in millihertz

        Example:
            >>> max_speed_mhz = stepper.get_max_speed_millihz()
        """
        __translation__ = "{0}->getMaxSpeedInMilliHz()"

    # ========== ACCELERATION CONTROL ==========

    def set_acceleration(self, acceleration: int) -> int:
        """
        Set acceleration in steps per second squared.

        Controls how quickly the motor ramps between speeds. Higher values
        mean faster acceleration but may lose steps if too aggressive.

        Valid range: > 0

        Args:
            acceleration (int): Acceleration in steps/second²

        Returns:
            int: 0 on success, -1 if acceleration <= 0

        Example:
            >>> stepper.set_acceleration(500)  # Ramp up 500 steps/s each second
        """
        __translation__ = "{0}->setAcceleration({1})"

    def get_acceleration(self) -> int:
        """
        Get configured acceleration.

        Returns the acceleration value that was set.

        Args:
            None

        Returns:
            int: Acceleration in steps/second²

        Example:
            >>> accel = stepper.get_acceleration()
        """
        __translation__ = "{0}->getAcceleration()"

    def get_current_acceleration(self) -> int:
        """
        Get current acceleration being applied.

        Returns the actual acceleration during ramping, or 0 when idle/coasting.
        Positive = accelerating forward, Negative = accelerating backward.

        Args:
            None

        Returns:
            int: Current acceleration in steps/second² (0 = not accelerating)

        Example:
            >>> current_accel = stepper.get_current_acceleration()
        """
        __translation__ = "{0}->getCurrentAcceleration()"

    def set_linear_acceleration(self, linear_accel_steps: int) -> None:
        """
        Set linear acceleration ramp-in.

        Creates a smooth transition into constant acceleration. Reduces mechanical
        stress by ramping acceleration linearly up from zero.

        Args:
            linear_accel_steps (int): Number of steps over which to ramp in acceleration

        Returns:
            None

        Example:
            >>> stepper.set_linear_acceleration(100)  # Ramp over 100 steps
        """
        __translation__ = "{0}->setLinearAcceleration({1})"

    def set_jump_start(self, jump_step: int) -> None:
        """
        Set jump start step for smoother motion from standstill.

        Allows starting from a non-zero ramp step, providing smoother initial
        acceleration from rest.

        Args:
            jump_step (int): Ramp step to start from

        Returns:
            None

        Example:
            >>> stepper.set_jump_start(10)
        """
        __translation__ = "{0}->setJumpStart({1})"

    def apply_speed_acceleration(self) -> None:
        """
        Apply new speed and acceleration values to current movement.

        Updates running motor with new speed/acceleration parameters without
        stopping. Useful for real-time speed adjustments.

        Args:
            None

        Returns:
            None

        Example:
            >>> stepper.set_speed_hz(1000)
            >>> stepper.apply_speed_acceleration()
        """
        __translation__ = "{0}->applySpeedAcceleration()"

    # ========== MOVEMENT COMMANDS ==========

    def move(self, steps: int, blocking: bool) -> dict[str, int]:
        """
        Move stepper by relative number of steps.

        If motor is running, updates the target relative to current target.
        Does not allow reversing direction of ongoing movement.

        Args:
            steps (int): Number of steps (positive = forward, negative = backward)
            blocking (bool): If True, wait for command to complete

        Returns:
            int: MoveResultCode (0 = MOVE_OK, other values = error)

        Example:
            >>> stepper.move(500)  # Move 500 steps forward
            >>> stepper.move(-100)  # Move 100 steps backward
        """
        __translation__ = "custom_stepper_move({0}, {1}, {2})"

    def move_to(self, position: int, blocking: bool) -> dict[str, int]:
        """
        Move stepper to absolute position.

        Sets target position for the motor. Motor will accelerate/decelerate
        as needed to reach target.

        Args:
            position (int): Target absolute position
            blocking (bool): If True, wait for command to complete

        Returns:
            int: MoveResultCode (0 = MOVE_OK, other values = error)

        Example:
            >>> stepper.move_to(5000)  # Move to position 5000
        """
        __translation__ = "custom_stepper_move_to({0}, {1}, {2})"

    def run_forward(self) -> dict[str, int]:
        """
        Run motor continuously forward.

        Motor will accelerate to set speed and continue until stopped.

        Args:
            None

        Returns:
            int: MoveResultCode (0 = MOVE_OK, other values = error)

        Example:
            >>> stepper.run_forward()
            >>> # ... later ...
            >>> stepper.stop_move()
        """
        __translation__ = "custom_stepper_run_forward({0})"

    def run_backward(self) -> dict[str, int]:
        """
        Run motor continuously backward.

        Motor will accelerate to set speed and continue until stopped.
        Requires direction pin to be configured.

        Args:
            None

        Returns:
            int: MoveResultCode (0 = MOVE_OK, other values = error)

        Example:
            >>> stepper.run_backward()
            >>> # ... later ...
            >>> stepper.stop_move()
        """
        __translation__ = "custom_stepper_run_backward({0})"

    def keep_running(self) -> None:
        """
        Keep running in current direction.

        Prevents motor from stopping; maintains current direction and acceleration.

        Args:
            None

        Returns:
            None

        Example:
            >>> stepper.keep_running()
        """
        __translation__ = "{0}->keepRunning()"

    def is_running_continuously(self) -> bool:
        """
        Check if motor is set to run continuously.

        Returns True if in continuous run mode (runForward/runBackward).

        Args:
            None

        Returns:
            bool: True if running continuously

        Example:
            >>> if stepper.is_running_continuously():
            ...     print("Motor is in continuous run mode")
        """
        __translation__ = "{0}->isRunningContinuously()"

    def forward_step(self, blocking: bool = False) -> None:
        """
        Execute single step forward.

        Performs one forward step immediately. Motor must not be moving.

        Args:
            blocking (bool): If True, wait for step to complete

        Returns:
            None

        Example:
            >>> stepper.forward_step()
        """
        __translation__ = "{0}->forwardStep({1})"

    def backward_step(self, blocking: bool = False) -> None:
        """
        Execute single step backward.

        Performs one backward step immediately. Motor must not be moving.
        Requires direction pin to be configured.

        Args:
            blocking (bool): If True, wait for step to complete

        Returns:
            None

        Example:
            >>> stepper.backward_step()
        """
        __translation__ = "{0}->backwardStep({1})"

    def move_by_acceleration(
        self, acceleration: int, allow_reverse: bool
    ) -> dict[str, int]:
        """
        Move by acceleration control (speed controlled via acceleration).

        Advanced mode where speed is controlled by applying acceleration or
        deceleration. Positive acceleration = accelerate forward to max speed.
        Negative acceleration = decelerate (or reverse if allow_reverse=True).

        Args:
            acceleration (int): Acceleration to apply (steps/second²)
            allow_reverse (bool): Allow motor to reverse direction

        Returns:
            int: MoveResultCode

        Example:
            >>> stepper.move_by_acceleration(1000)  # Accelerate forward
            >>> stepper.move_by_acceleration(-500)  # Decelerate
        """
        __translation__ = "custom_stepper_move_by_acceleration({0}, {1}, {2})"

    def stop_move(self) -> None:
        """
        Stop motor with normal deceleration.

        Initiates smooth stop using configured acceleration. Motor will
        decelerate to zero. Safe to call from interrupt.

        Args:
            None

        Returns:
            None

        Example:
            >>> stepper.stop_move()
        """
        __translation__ = "{0}->stopMove()"

    def is_stopping(self) -> bool:
        """
        Check if motor is decelerating to stop.

        Returns True while motor is decelerating after stopMove() call.

        Args:
            None

        Returns:
            bool: True if decelerating

        Example:
            >>> if stepper.is_stopping():
            ...     print("Motor is slowing down")
        """
        __translation__ = "{0}->isStopping()"

    def force_stop(self) -> None:
        """
        Stop motor immediately without deceleration.

        Abruptly halts motor. Position may be lost due to queue flush.
        Safe to call from interrupt. Motor stops within ~20ms.

        Args:
            None

        Returns:
            None

        Example:
            >>> stepper.force_stop()
        """
        __translation__ = "{0}->forceStop()"

    def force_stop_and_new_position(self, new_pos: int) -> None:
        """
        Stop immediately and set new position.

        Abruptly stops motor and updates internal position counter.
        Used when external sensor provides new position.

        Args:
            new_pos (int): New position value to set

        Returns:
            None

        Example:
            >>> stepper.force_stop_and_new_position(0)
        """
        __translation__ = "{0}->forceStopAndNewPosition({1})"

    def steps_to_stop(self) -> int:
        """
        Get steps needed to decelerate to stop.

        Calculates how many more steps the motor will take before reaching
        zero speed if stopMove() is called now. Useful for obstacle avoidance.

        Args:
            None

        Returns:
            int: Number of steps to stop

        Example:
            >>> remaining = stepper.steps_to_stop()
            >>> if stepper.get_current_position() + remaining > limit:
            ...     stepper.stop_move()
        """
        __translation__ = "{0}->stepsToStop()"

    # ========== POSITION QUERIES ==========

    def get_current_position(self) -> int:
        """
        Get current motor position.

        Returns the internal position counter reflecting executed steps.

        Args:
            None

        Returns:
            int: Current position in steps

        Example:
            >>> pos = stepper.get_current_position()
        """
        __translation__ = "{0}->getCurrentPosition()"

    def get_target_position(self) -> int:
        """
        Get target position for current move.

        Returns the position the motor is moving toward.

        Args:
            None

        Returns:
            int: Target position in steps

        Example:
            >>> target = stepper.get_target_position()
        """
        __translation__ = "{0}->targetPos()"

    def set_current_position(self, position: int) -> None:
        """
        Manually set the current position.

        Changes the motor's internal position counter to the specified value.
        Useful for calibration or when using external position feedback sensors.
        Recommend using only while motor is stopped.

        Args:
            position (int): New position value

        Returns:
            None

        Example:
            >>> stepper.set_current_position(0)  # Reset to origin
        """
        __translation__ = "{0}->setCurrentPosition({1})"

    def distance_to_go(self) -> int:
        """
        Get remaining distance to target position.

        Returns the number of steps between current position and target position.
        Positive means target is ahead, negative means behind.

        Args:
            None

        Returns:
            int: Steps remaining (can be negative)

        Example:
            >>> remaining = stepper.distance_to_go()
            >>> if remaining == 0:
            ...     print("Motor reached target")
        """
        __translation__ = (
            "{0}->getPositionAfterCommandsCompleted() - {0}->getCurrentPosition()"
        )

    # ========== STATUS QUERIES ==========

    def is_running(self) -> bool:
        """
        Check if motor is currently moving.

        Returns True while the motor has commanded position different from
        current position and is executing steps. Returns False when idle.
        Essential for non-blocking operation.

        Args:
            None

        Returns:
            bool: True if motor is moving, False if idle

        Example:
            >>> stepper.move_to(5000)
            >>> while stepper.is_running():
            ...     # Do other work while motor moves
            ...     pass
        """
        __translation__ = "{0}->isRunning()"

    def ticks_in_queue(self) -> int:
        """
        Get number of CPU ticks queued for execution.

        Returns the cumulative ticks queued for future execution. Useful for
        monitoring queue depth and ensuring sufficient lookahead for smooth motion.

        Args:
            None

        Returns:
            int: Number of ticks in command queue

        Example:
            >>> queue_ticks = stepper.ticks_in_queue()
        """
        __translation__ = "{0}->ticksInQueue()"

    def has_ticks_in_queue(self, min_ticks: int) -> bool:
        """
        Check if command queue has minimum ticks pending.

        Returns True if there are at least min_ticks queued for future execution.

        Args:
            min_ticks (int): Minimum ticks to check for

        Returns:
            bool: True if queue has at least min_ticks pending

        Example:
            >>> if stepper.has_ticks_in_queue(1000):
            ...     print("Queue is well-stocked")
        """
        __translation__ = "{0}->hasTicksInQueue({1})"

    def queue_entries(self) -> int:
        """
        Get number of command queue entries in use.

        Returns the count of command entries currently in the queue.
        Each command can contain multiple steps. Queue depth varies by platform
        (typically 16-32 entries).

        Args:
            None

        Returns:
            int: Number of queue entries in use

        Example:
            >>> entries = stepper.queue_entries()
        """
        __translation__ = "{0}->queueEntries()"

    def get_period_after_commands_us(self) -> int:
        """
        Get time in microseconds until queue completion.

        Returns the estimated time needed to execute all queued commands.
        Useful for synchronizing with other tasks or scheduling the next
        movement command.

        Args:
            None

        Returns:
            int: Time in microseconds until queue is empty

        Example:
            >>> wait_time_us = stepper.get_period_after_commands_us()
        """
        __translation__ = "{0}->getPeriodInUsAfterCommandsCompleted()"

    def get_period_after_commands_ticks(self) -> int:
        """
        Get time in CPU ticks until queue completion.

        Returns the estimated time needed to execute all queued commands,
        expressed in CPU ticks.

        Args:
            None

        Returns:
            int: Time in CPU ticks until queue is empty

        Example:
            >>> wait_time_ticks = stepper.get_period_after_commands_ticks()
        """
        __translation__ = "{0}->getPeriodInTicksAfterCommandsCompleted()"

    def get_position_after_commands_completed(self) -> int:
        """
        Get position after all queued commands complete.

        Returns where the motor will be positioned after executing all
        currently queued commands.

        Args:
            None

        Returns:
            int: Future position in steps

        Example:
            >>> future_pos = stepper.get_position_after_commands_completed()
        """
        __translation__ = "{0}->getPositionAfterCommandsCompleted()"

    def set_position_after_commands_completed(self, new_pos: int) -> None:
        """
        Set future position after queued commands complete.

        Updates the internal position that will be set after current command
        queue drains. Takes immediate effect on getCurrentPosition().

        Args:
            new_pos (int): Position value to set after queue completes

        Returns:
            None

        Example:
            >>> stepper.set_position_after_commands_completed(0)
        """
        __translation__ = "{0}->setPositionAfterCommandsCompleted({1})"

    # ========== RAMP STATE QUERIES ==========

    def ramp_state(self) -> int:
        """
        Get current ramp generator state.

        Returns state flags indicating current ramp state and direction.
        Advanced users only.

        Args:
            None

        Returns:
            int: State flags (RAMP_STATE_... and RAMP_DIRECTION_... combined)

        Example:
            >>> state = stepper.ramp_state()
        """
        __translation__ = "{0}->rampState()"

    def is_ramp_generator_active(self) -> bool:
        """
        Check if ramp generator is active.

        Returns True while acceleration/deceleration is being calculated.

        Args:
            None

        Returns:
            bool: True if ramp generator is running

        Example:
            >>> if stepper.is_ramp_generator_active():
            ...     print("Motor is accelerating/decelerating")
        """
        __translation__ = "{0}->isRampGeneratorActive()"

    # ========== MOTOR CONTROL ==========

    def enable_outputs(self) -> bool:
        """
        Enable motor driver outputs.

        Energizes the motor, allowing it to hold torque. Used with manual
        enable control (when auto_enable is False).

        Args:
            None

        Returns:
            bool: True if successfully enabled

        Example:
            >>> stepper.enable_outputs()
        """
        __translation__ = "{0}->enableOutputs()"

    def disable_outputs(self) -> bool:
        """
        Disable motor driver outputs.

        De-energizes the motor, reducing power consumption. Motor loses holding
        torque but can still be rotated manually. Used with manual enable control.

        Args:
            None

        Returns:
            bool: True if successfully disabled

        Example:
            >>> stepper.disable_outputs()
        """
        __translation__ = "{0}->disableOutputs()"

    # ========== ADVANCED CONFIGURATION ==========

    def set_forward_planning_time_ms(self, ms: int) -> None:
        """
        Configure forward planning horizon (advanced users only).

        Sets how far ahead the acceleration planner looks. Longer horizon provides
        smoother acceleration curves but increases latency to speed changes.
        Default is 20ms. Only change if stepper is not running.

        Attention: This is for advanced users only. Too small values risk the
        stepper running at full speed then stopping abruptly due to queue underrun.

        Args:
            ms (int): Planning horizon in milliseconds

        Returns:
            None

        Example:
            >>> stepper.set_forward_planning_time_ms(30)
        """
        __translation__ = "{0}->setForwardPlanningTimeInMs({1})"

    def detach_from_pin(self) -> None:
        """
        Detach stepper from its pin (advanced).

        Releases the step pin for other use. Pretty low-level, use with care.

        Args:
            None

        Returns:
            None

        Example:
            >>> stepper.detach_from_pin()
        """
        __translation__ = "{0}->detachFromPin()"

    def reattach_to_pin(self) -> None:
        """
        Reattach stepper to its pin (advanced).

        Restores stepper control after detachFromPin(). Pretty low-level, use with care.

        Args:
            None

        Returns:
            None

        Example:
            >>> stepper.reattach_to_pin()
        """
        __translation__ = "{0}->reAttachToPin()"

    # ========== ESP32 PULSE COUNTER (ESP32 only) ==========

    def attach_to_pulse_counter(
        self,
        unused_pcnt_unit: int,
        low_value: int,
        high_value: int,
    ) -> bool:
        """
        Attach stepper to pulse counter for position verification (ESP32 only, advanced).

        Connects an independent pulse counter to track steps and verify
        correct execution. Used for testing and quality assurance.

        Note: The pcnt_unit parameter is ignored on IDF5; units are managed by the system.

        Args:
            unused_pcnt_unit (int): Pulse counter unit (ignored on IDF5, for compatibility)
            low_value (int): Low counter limit (default -16384)
            high_value (int): High counter limit (default 16384)
            dir_pin_readback (int): Optional direction pin for readback

        Returns:
            bool: True on success, False on error

        Example:
            >>> stepper.attach_to_pulse_counter()
            >>> stepper.attach_to_pulse_counter(low_value=-3200, high_value=3200)
        """
        __translation__ = "{0}->attachToPulseCounter({1}, {2}, {3})"

    def read_pulse_counter(self) -> int:
        """
        Read current pulse counter value (ESP32 only).

        Returns the current value of the attached pulse counter.

        Args:
            None

        Returns:
            int: Current pulse counter value

        Example:
            >>> count = stepper.read_pulse_counter()
        """
        __translation__ = "{0}->readPulseCounter()"

    def clear_pulse_counter(self) -> None:
        """
        Clear pulse counter to zero (ESP32 only).

        Resets the pulse counter to 0.

        Args:
            None

        Returns:
            None

        Example:
            >>> stepper.clear_pulse_counter()
        """
        __translation__ = "{0}->clearPulseCounter()"

    def pulse_counter_attached(self) -> bool:
        """
        Check if pulse counter is attached (ESP32 only).

        Returns True if a pulse counter is currently attached.

        Args:
            None

        Returns:
            bool: True if pulse counter attached

        Example:
            >>> if stepper.pulse_counter_attached():
            ...     print("Pulse counter is active")
        """
        __translation__ = "{0}->pulseCounterAttached()"
