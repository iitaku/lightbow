import time
import math
import random
import gc
import digitalio
import board
from rainbowio import colorwheel
import neopixel

def mix(color_1, color_2, weight_2):
    """
    Blend between two colors with a given ratio.
    @param color_1:  first color, as an (r,g,b) tuple
    @param color_2:  second color, as an (r,g,b) tuple
    @param weight_2: Blend weight (ratio) of second color, 0.0 to 1.0
    @return: (r,g,b) tuple, blended color
    """
    if weight_2 < 0.0:
        weight_2 = 0.0
    elif weight_2 > 1.0:
        weight_2 = 1.0
    weight_1 = 1.0 - weight_2
    return (int(color_1[0] * weight_1 + color_2[0] * weight_2),
            int(color_1[1] * weight_1 + color_2[1] * weight_2),
            int(color_1[2] * weight_1 + color_2[2] * weight_2))

PIXEL_PIN = board.A1
NUM_PIXELS = 30

strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=1.0, auto_write=False)
strip.fill(0)
strip.show()

def color_off():
    vs = [0] * NUM_PIXELS
    vs[0] = (255, 255, 255)
    vs[1] = (255, 255, 255)
    return vs

def color_mono(c):
    return [c] * NUM_PIXELS

def color_gradation(c1, c2):
    vs = []
    for i in range(NUM_PIXELS):
        vs.append(mix(c1, c2, math.pow(i/NUM_PIXELS, 3)))
    return vs

def color_step(cs, n):
    vs = []
    for i in range(0, NUM_PIXELS, n):
        for j in range(0, n):
            vs.append(cs[int(i/n) % len(cs)])
    return vs

mode = 0
colors = []
colors.append(color_off())
# colors.append(color_mono((0, 255, 0))) # Green
# colors.append(color_mono((255, 0, 0))) # Red
# colors.append(color_mono((255, 255, 255))) # Silver
# colors.append(color_mono((255, 120, 0))) # Gold
# colors.append(color_gradation((0, 0, 255), (255, 255, 255))) # Snow 
colors.append(color_gradation((255, 20, 50), (252, 50, 150))) # Cherry blossom 
# colors.append(color_step(((50, 0, 0), (0, 50, 0)), 8))

def power(duration, reverse):
    """
    Animate NeoPixels with accompanying for power on / off.
    @param duration: estimated duration of sound, in seconds (>0.0)
    @param reverse:  if True, do power-off effect (reverses animation)
    """
    if reverse:
        prev = NUM_PIXELS
    else:
        prev = 0
    gc.collect()                   # Tidy up RAM now so animation's smoother
    start_time = time.monotonic()  # Save audio start time
    while True:
        elapsed = time.monotonic() - start_time  # Time spent playing sound
        if elapsed > duration:                   # Past sound duration?
            break                                # Stop animating
        fraction = elapsed / duration            # Animation time, 0.0 to 1.0
        if reverse:
            fraction = 1.0 - fraction            # 1.0 to 0.0 if reverse
        fraction = math.pow(fraction, 0.5)       # Apply nonlinear curve
        threshold = int(NUM_PIXELS * fraction + 0.5)
        num = threshold - prev # Number of pixels to light on this pass
        if num != 0:
            if reverse:
                strip[threshold:prev] = [0] * -num
            else:
                for i in range(num):
                    strip[prev+i] = colors[mode][prev+i]
            strip.show()
            # NeoPixel writes throw off time.monotonic() ever so slightly
            # because interrupts are disabled during the transfer.
            # We can compensate somewhat by adjusting the start time
            # back by 30 microseconds per pixel.
            start_time -= NUM_PIXELS * 0.00003
            prev = threshold

    # At end, ensure strip is off except first two to prevent battery sleep
    strip[0] = (255, 255, 255)
    strip[1] = (255, 255, 255)

    strip.show()

switch = digitalio.DigitalInOut(board.A2)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.DOWN

power(1.2, False)

elapsed = 0
start_time = time.monotonic()
while True:
    if switch.value:
        elapsed = time.monotonic() - start_time
    else:
        start_time = time.monotonic()
        # elapsed = 0

    if elapsed > 1:
        mode = (mode + 1) % len(colors)
        power(1.2, False)
        elapsed = 0
        start_time = time.monotonic()