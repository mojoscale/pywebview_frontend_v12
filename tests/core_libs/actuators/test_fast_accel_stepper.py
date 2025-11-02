import actuators.fast_accel_stepper as fas


engine = fas.FastAccelStepperEngine()


def setup() -> None:
    engine.init()

    stepper = engine.stepper_connect_to_pin(6)

    if stepper:
        print("=== PIN CONFIGURATION ===")

        # Direction pin setup
        stepper.set_direction_pin(9)
        stepper.set_direction_pin(9)
        dir_pin = stepper.get_direction_pin()
        print(f"Direction pin: {dir_pin}")

        direction_counts_up = stepper.direction_pin_high_counts_up()
        print(f"HIGH counts up: {direction_counts_up}")

        # Enable pin setup

        stepper.set_enable_pin(10)
        enable_low = stepper.get_enable_pin_low_active()
        enable_high = stepper.get_enable_pin_high_active()
        print(f"Enable pin (low-active): {enable_low}")
        print(f"Enable pin (high-active): {enable_high}")

        # Auto-enable setup
        stepper.set_auto_enable(True)
        stepper.set_delay_to_enable(500)  # 500 microseconds
        stepper.set_delay_to_disable(10)  # 10 milliseconds

        print("=== SPEED CONTROL ===")

        # Set speed in different units
        result_hz = stepper.set_speed_hz(500)
        print(f"Set speed 500 Hz: {result_hz}")

        result_us = stepper.set_speed_us(2000)
        print(f"Set speed 2000 us/step: {result_us}")

        result_ticks = stepper.set_speed_ticks(3200)
        print(f"Set speed 3200 ticks/step: {result_ticks}")

        result_millihz = stepper.set_speed_millihz(100)
        print(f"Set speed 100 milliHz: {result_millihz}")

        # Get configured speed
        speed_us = stepper.get_speed_us()
        speed_ticks = stepper.get_speed_ticks()
        speed_millihz = stepper.get_speed_millihz()
        print(
            f"Configured speed: {speed_us} us, {speed_ticks} ticks, {speed_millihz} mHz"
        )

        # Get current speed (actual, accounting for acceleration)
        current_speed_us = stepper.get_current_speed_us()
        current_speed_millihz = stepper.get_current_speed_millihz()
        print(f"Current speed: {current_speed_us} us, {current_speed_millihz} mHz")

        # Get max hardware speed
        max_hz = stepper.get_max_speed_hz()
        max_us = stepper.get_max_speed_us()
        max_ticks = stepper.get_max_speed_ticks()
        max_millihz = stepper.get_max_speed_millihz()
        print(
            f"Max speed: {max_hz} Hz, {max_us} us, {max_ticks} ticks, {max_millihz} mHz"
        )

        print("=== ACCELERATION CONTROL ===")

        # Set acceleration
        result_accel = stepper.set_acceleration(500)
        print(f"Set acceleration 500 steps/s square: {result_accel}")

        accel = stepper.get_acceleration()
        print(f"Configured acceleration: {accel} steps/s square")

        current_accel = stepper.get_current_acceleration()
        print(f"Current acceleration: {current_accel} steps/s square")

        # Linear acceleration and jump start
        stepper.set_linear_acceleration(100)
        stepper.set_jump_start(10)

        # Apply new speed/acceleration to current movement
        stepper.apply_speed_acceleration()

        print("=== MOVEMENT COMMANDS ===")

        # Relative movement
        move_result = stepper.move(1000)
        print(f"Move 1000 steps: {move_result}")

        # Absolute positioning
        moveto_result = stepper.move_to(5000)
        print(f"Move to position 5000: {moveto_result}")

        # Continuous running
        run_fwd = stepper.run_forward()
        print(f"Run forward: {run_fwd}")

        # (in real use, you'd wait here)
        stepper.stop_move()

        run_bwd = stepper.run_backward()
        print(f"Run backward: {run_bwd}")

        stepper.stop_move()
        stepper.keep_running()

        is_continuous = stepper.is_running_continuously()
        print(f"Running continuously: {is_continuous}")

        # Single steps
        stepper.forward_step()
        stepper.backward_step()

        # Move by acceleration (speed control via acceleration)
        accel_move = stepper.move_by_acceleration(1000, allow_reverse=False)
        print(f"Move by acceleration: {accel_move}")

        print("=== STOP CONTROL ===")

        # Stop with deceleration
        stepper.stop_move()
        is_motor_stopping = stepper.is_stopping()
        print(f"Is stopping: {is_motor_stopping}")

        steps_stop = stepper.steps_to_stop()
        print(f"Steps to stop: {steps_stop}")

        # Force stop (abrupt)
        stepper.force_stop()

        # Force stop and set new position
        stepper.force_stop_and_new_position(0)

        # Current position
        current_pos = stepper.get_current_position()
        print(f"Current position: {current_pos}")

        # Target position
        target_pos = stepper.get_target_position()
        print(f"Target position: {target_pos}")

        # Set current position
        stepper.set_current_position(0)

        # Distance to go
        distance = stepper.distance_to_go()
        print(f"Distance to go: {distance}")

        # Future position after queue completes
        future_pos = stepper.get_position_after_commands_completed()
        print(f"Position after commands complete: {future_pos}")

        stepper.set_position_after_commands_completed(0)

        # Running status
        is_motor_running = stepper.is_running()
        print(f"Is running: {is_motor_running}")

        # Queue information
        ticks_queue = stepper.ticks_in_queue()
        print(f"Ticks in queue: {ticks_queue}")

        has_ticks = stepper.has_ticks_in_queue(1000)
        print(f"Has at least 1000 ticks: {has_ticks}")

        entries = stepper.queue_entries()
        print(f"Queue entries: {entries}")

        # Time until queue completes
        period_us = stepper.get_period_after_commands_us()
        period_ticks = stepper.get_period_after_commands_ticks()
        print(f"Time to queue complete: {period_us} us, {period_ticks} ticks")

        # Ramp generator state
        ramp_state_motor = stepper.ramp_state()
        print(f"Ramp state: {ramp_state_motor}")

        is_ramp_active = stepper.is_ramp_generator_active()
        print(f"Ramp generator active: {is_ramp_active}")

        # Manual enable/disable
        enabled = stepper.enable_outputs()
        print(f"Outputs enabled: {enabled}")

        disabled = stepper.disable_outputs()
        print(f"Outputs disabled: {disabled}")

        # Forward planning time (advanced)
        stepper.set_forward_planning_time_ms(20)

        # Pin attach/detach (advanced)
        stepper.detach_from_pin()
        stepper.reattach_to_pin()

        # Pulse counter attachment
        pulse_attached = stepper.attach_to_pulse_counter()
        print(f"Pulse counter attached: {pulse_attached}")

        # Read pulse counter
        pulse_count = stepper.read_pulse_counter()
        print(f"Pulse counter value: {pulse_count}")

        # Clear pulse counter
        stepper.clear_pulse_counter()

        # Check if pulse counter is attached
        is_pulse_attached = stepper.pulse_counter_attached()
        print(f"Pulse counter still attached: {is_pulse_attached}")

        # Reset and configure
        stepper.set_current_position(0)
        stepper.set_speed_hz(1000)
        stepper.set_acceleration(500)
        stepper.set_auto_enable(True)
        stepper.set_delay_to_enable(500)
        stepper.set_delay_to_disable(100)

        # Move sequence
        positions = [1000, 3000, 2000, 0]

        for target in positions:
            stepper.move_to(target, False)
            print(f"Moving to {target}...")

            # Wait for movement to complete (non-blocking check)
            while stepper.is_running():
                # Do other work here
                pass

            final_pos = stepper.get_current_position()
            print(f"Reached position: {final_pos}")

        # Start continuous motion
        stepper.run_forward()
        print("Running forward...")

        # Adjust speed during motion
        speeds = [500, 1000, 2000, 1000, 500]

        for speed in speeds:
            stepper.set_speed_hz(speed)
            stepper.apply_speed_acceleration()
            print(f"Speed adjusted to {speed} Hz")
            # In real code, would sleep/delay here

        stepper.stop_move()
        print("Motion stopped")

    else:
        print("Failed to connect stepper to pin")


def loop() -> None:
    pass
