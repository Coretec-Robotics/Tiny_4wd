#!/usr/bin/env python
# coding: Latin-1

# Control a Tiny4WD using a bluetooth keyboard or a joypad that pretends to be a bluetooth keyboard e.g. http://www.8bitdo.com/zero/

# wayne@thebubbleworks.com

# evdev keyboard handling from https://gpiozero.readthedocs.io/en/stable/recipes.html#keyboard-controlled-robot

# First, pair a bluetooth keyboard (or gamepad that is really a keyboard, such as the Z8BitDo ero) on the Pi's desktop first.


# You may need to install these  Python dependencies:
# sudo pip3 install evdev
# sudo pip3 install explorerhat


# Note: This uses the first keyboard found, so to be sure to have only a single bluetooth keyboard or 8bitdo Zero connected.
#       e.g. disconnect any USB keyboard, if you needed.

# if you see the following error then there is liekly no keyboard connected at all:

#       IndexError: list index out of range


# Load library functions we want
from evdev import InputDevice, list_devices, ecodes
from explorerhat import motor


# Depends on which way round your wires are to the motors, one or both of these may need to be a negative number
LEFT_MOTOR_MAX_POWER_FWD  = 100
RIGHT_MOTOR_MAX_POWER_FWD = 100

# Depending on which side of your robot motors are mounted these might need swapping
left_motor = motor.one
right_motor = motor.two


def get_keyboard(keyboard_index = 0):

    # Get the list of available input devices
    devices = [InputDevice(device) for device in list_devices()]
    # Filter out everything that's not a keyboard. Keyboards are defined as any
    # device which has keys, and which specifically has keys 1..31 (roughly Esc,
    # the numeric keys, the first row of QWERTY plus a few more) and which does
    # *not* have key 0 (reserved)
    must_have = {i for i in range(1, 32)}
    must_not_have = {0}
    devices = [
        dev
        for dev in devices
        for keys in (set(dev.capabilities().get(ecodes.EV_KEY, [])),)
        if must_have.issubset(keys)
        and must_not_have.isdisjoint(keys)
    ]
    return devices[keyboard_index]



# Motor Control

def forward():
    left_motor.speed(LEFT_MOTOR_MAX_POWER_FWD)
    right_motor.speed(RIGHT_MOTOR_MAX_POWER_FWD)

def backward():
    left_motor.speed(-LEFT_MOTOR_MAX_POWER_FWD)
    right_motor.speed(-RIGHT_MOTOR_MAX_POWER_FWD)

def left():
    left_motor.speed(-LEFT_MOTOR_MAX_POWER_FWD)
    right_motor.speed( RIGHT_MOTOR_MAX_POWER_FWD)

def right():
    left_motor.speed( LEFT_MOTOR_MAX_POWER_FWD)
    right_motor.speed(-RIGHT_MOTOR_MAX_POWER_FWD)


def stop():
    left_motor.speed(0)
    right_motor.speed(0)


keypress_actions = {
    # Arrow keys:
    ecodes.KEY_UP: forward,
    ecodes.KEY_DOWN: backward,
    ecodes.KEY_LEFT: left,
    ecodes.KEY_RIGHT: right,

    # 8BitDo Zero 'keys'
    ecodes.KEY_C: forward,
    ecodes.KEY_D: backward,
    ecodes.KEY_E: left,
    ecodes.KEY_F: right,
}


try:
    print('Press CTRL+C to quit')
    keyboard = get_keyboard()

    for event in keyboard.read_loop():
        if event.type == ecodes.EV_KEY and event.code in keypress_actions:
            if event.value == 1:  # key down
                keypress_actions[event.code]()
            if event.value == 0:  # key up
                stop()

except KeyboardInterrupt:
    # CTRL+C exit, disable all motors
    print("stopping...")

motor.stop()
print("Bye")

