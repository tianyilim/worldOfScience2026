"""
Pi Servo module.
"""
import time

import RPi.GPIO as GPIO


OUT_PIN = 11
PULSE_FREQ = 50

GPIO.setmode(GPIO.BOARD)
GPIO.setup(OUT_PIN, GPIO.OUT)


def main():

    servo1 = GPIO.PWM(OUT_PIN, PULSE_FREQ)
    servo1.start(0)

    try:
        while True:
            print("Enter angle to set to:")
            angle = input()
            angle = min(max(int(angle), 0), 180)
            print("Setting angle to", angle)

            duty_cycle = 2 + (angle / 180) * 10
            servo1.ChangeDutyCycle(duty_cycle)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Ctrl+C pressed. Exiting.")
    except Exception as e:
        print("Error:", e)

    servo1.stop()
    GPIO.cleanup()


if __name__ == "__main__":
    main()
