import time
import math
import random
import gc
import digitalio
import board
from rainbowio import colorwheel
import neopixel

# CUSTOMIZE YOUR COLOR HERE:
# (red, green, blue) -- each 0 (off) to 255 (brightest)
# COLOR = (255, 0, 0)  # red
# COLOR = (100, 0, 255)  # purple
#COLOR = (0, 100, 255) #cyan
# COLOR = (255, 0, 0) #green
COLOR = (0, 255, 0) #green

PIXEL_PIN = board.A1
NUM_PIXELS = 30

strip = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.3, auto_write=False)
strip.fill(0)
strip.show()
 
# "Idle" color is 1/4 brightness, "swinging" color is full brightness...
COLOR_IDLE = (int(COLOR[0] / 1), int(COLOR[1] / 1), int(COLOR[2] / 1))
COLOR_SWING = COLOR
COLOR_HIT = (255, 255, 255)  # "hit" color is white

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
                strip[prev:threshold] = [COLOR_IDLE] * num
            strip.show()
            # NeoPixel writes throw off time.monotonic() ever so slightly
            # because interrupts are disabled during the transfer.
            # We can compensate somewhat by adjusting the start time
            # back by 30 microseconds per pixel.
            start_time -= NUM_PIXELS * 0.00003
            prev = threshold

    if reverse:
        strip.fill(0)                            # At end, ensure strip is off
    else:
        strip.fill(COLOR_IDLE)                   # or all pixels set on
    strip.show()

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

switch = digitalio.DigitalInOut(board.A2)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.DOWN

state = False

power(1.2, False)

# i = 0
while True:

    # strip.brightness = 0.3 + math.sin(math.radians(i)) * 0.1
    # strip.show()
    # i += 1

    if switch.value:
        state = not state
        power(1.2, state)
    
