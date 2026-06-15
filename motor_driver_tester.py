"""
Pi Servo module.
"""
import time

import RPi.GPIO as GPIO

MOTOR_1_OUT_PIN_A = 32
MOTOR_1_OUT_PIN_B = 36
MOTOR_2_OUT_PIN_A = 38
MOTOR_2_OUT_PIN_B = 40

PULSE_FREQ = 50

GPIO.setmode(GPIO.BOARD)
GPIO.setup(MOTOR_1_OUT_PIN_A, GPIO.OUT)
GPIO.setup(MOTOR_1_OUT_PIN_B, GPIO.OUT)
GPIO.setup(MOTOR_2_OUT_PIN_A, GPIO.OUT)
GPIO.setup(MOTOR_2_OUT_PIN_B, GPIO.OUT)


def move_motor(pin_a, pin_b, is_forward: bool = True, speed: float = 0):
    speed = min(100, max(0, speed))
    if is_forward:
        pin_a.ChangeDutyCycle(speed)
        pin_b.ChangeDutyCycle(0)
    else:
        pin_a.ChangeDutyCycle(0)
        pin_b.ChangeDutyCycle(speed)


def main():
    motor_1_a = GPIO.PWM(MOTOR_1_OUT_PIN_A, PULSE_FREQ)
    motor_1_b = GPIO.PWM(MOTOR_1_OUT_PIN_B, PULSE_FREQ)
    motor_2_a = GPIO.PWM(MOTOR_2_OUT_PIN_A, PULSE_FREQ)
    motor_2_b = GPIO.PWM(MOTOR_2_OUT_PIN_B, PULSE_FREQ)
    motor_1_a.start(0)
    motor_1_b.start(0)
    motor_2_a.start(0)
    motor_2_b.start(0)

    print("Spinning")

    for label, motor_ab in (
        ("Motor 1", (motor_1_a, motor_1_b)),
        ("Motor 2", (motor_2_a, motor_2_b))
    ):
        print("-" * 100)
        print("Motor:", label)

        # Move motor forward, increase speed
        for speed in range(11):
            motor_a, motor_b = motor_ab
            out_speed = speed * 10
            print("Forward with speed", out_speed)
            move_motor(motor_a, motor_b, True, out_speed)
            time.sleep(0.1)
        for speed in range(11):
            motor_a, motor_b = motor_ab
            out_speed = (10-speed) * 10
            print("Forward with speed", out_speed)
            move_motor(motor_a, motor_b, True, out_speed)
            time.sleep(0.1)
        # Move motor backward, increase speed
        for speed in range(11):
            motor_a, motor_b = motor_ab
            out_speed = speed * 10
            print("Backward with speed", out_speed)
            move_motor(motor_a, motor_b, False, out_speed)
            time.sleep(0.1)
        for speed in range(11):
            motor_a, motor_b = motor_ab
            out_speed = (10-speed) * 10
            print("Backward with speed", out_speed)
            move_motor(motor_a, motor_b, False, out_speed)
            time.sleep(0.1)

    move_motor(motor_1_a, motor_1_b, True, 0.0)
    move_motor(motor_2_a, motor_2_b, True, 0.0)

    print("Stopping motor_1_a")
    motor_1_a.stop()
    print("Stopping motor_1_b")
    motor_1_b.stop()
    print("Stopping motor_2_a")
    motor_2_a.stop()
    print("Stopping motor_2_b")
    motor_2_b.stop()

    print("Cleanup")
    GPIO.cleanup([
        MOTOR_1_OUT_PIN_A,
        MOTOR_1_OUT_PIN_B,
        MOTOR_2_OUT_PIN_A,
        MOTOR_2_OUT_PIN_B
    ])


if __name__ == "__main__":
    main()
