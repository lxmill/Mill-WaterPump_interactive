import board
import digitalio
import time
import pwmio
import touchio

from adafruit_debouncer import Debouncer, Button

import neopixel
from rainbowio import colorwheel


def RingColorWheel(delay, Pixel, Color):
    time.sleep(delay)
    for i in range(16):
        Pixel[i] = colorwheel(Color)


def RingColorStatic(Pixel, Color):
    time.sleep(0.01)
    for i in range(16):
        Pixel[i] = Color

# millPower = digitalio.DigitalInOut(board.D8)
# millPower.direction = digitalio.Direction.OUTPUT

millPower = pwmio.PWMOut(board.D8, frequency=5000, duty_cycle=0)

waterPower = digitalio.DigitalInOut(board.D9)
waterPower.direction = digitalio.Direction.OUTPUT

THRESHOLD_1 = 500  ## HAS TO BE CALIBRATED WHEN FULLY MOUNTED
t1 = touchio.TouchIn(board.D0)
t1.threshold = t1.raw_value + THRESHOLD_1
touchpad_1 = Button(t1, value_when_pressed=True)

THRESHOLD_2 = 500  ## HAS TO BE CALIBRATED WHEN FULLY MOUNTED
t2 = touchio.TouchIn(board.D1)
t2.threshold = t2.raw_value + THRESHOLD_2
touchpad_2 = Button(t2, value_when_pressed=True)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

NeoPixel = neopixel.NeoPixel(board.D10, 16)

NeoPixel.brightness = 0.75

color_value = 0

LeftHand = False
RightHand = False

watertime_refresh = time.monotonic()

while True:
    
    touchpad_1.update()
    touchpad_2.update()

    if not RightHand and not LeftHand:
        RingColorWheel(0.01, NeoPixel, color_value)
        color_value += 1
        if color_value == 256:
            color_value = 0

    if touchpad_1.rose:
        print("Touch_1 On")
        LeftHand = True
        # millPower.value = True
        millPower.duty_cycle = 32768

    if touchpad_1.fell:
        print("Touch_1 Off")
        LeftHand = False
        # millPower.value = False
        millPower.duty_cycle = 0

    if touchpad_2.rose:
        print("Touch_2 On")
        RightHand = True
        watertime_refresh = time.monotonic()

    if touchpad_2.fell:
        print("Touch_2 Off")
        RightHand = False
        waterPower.value = False

    if LeftHand and not RightHand:
        RingColorStatic(NeoPixel, (255, 255, 255))

    if RightHand and not LeftHand:
        RingColorStatic(NeoPixel, (0, 0, 255))

    if RightHand and LeftHand:
        RingColorStatic(NeoPixel, (0, 255, 0))

    if (time.monotonic() - watertime_refresh) > 3 and RightHand:
        try:
            waterPower.value = True
            watertime_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue
