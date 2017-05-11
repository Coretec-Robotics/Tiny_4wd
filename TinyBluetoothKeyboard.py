#!/usr/bin/env python
# coding: Latin-1

# Control a Tiny4WD using a bluetooth keyboard or a joypad that pretends to be a bluetooth keyboard e.g. http://www.8bitdo.com/zero/

# wayne@thebubbleworks.com

# evdev keyboard handling based on example from https://gpiozero.readthedocs.io/en/stable/recipes.html#keyboard-controlled-robot

# First, pair a bluetooth keyboard (or gamepad that is really a keyboard, such as the Z8BitDo ero) on the Pi's desktop first.

# Alternatively, to pair a bluetooth keyboard using a Terminal or SSH, the steps are:

# -- Run:
#
# bluetoothctl

# -- This wil start a 'bluetooth command shell', enter these commands:

# power on
# agent on
# scan on

# -- You should eventually, be patient, see something like:   [NEW] Device 97:13:70:C5:AA:BB Bluetooth  Keyboard
# -- The value 97:13:70:C5:AA:BB will be different and use your value in place of <MACADDRESS> below:

# connect <MACADDRESS>
# trust  <MACADDRESS>
# pair <MACADDRESS>

# -- You should see something like:  [agent] PIN code: 967776
# -- type the code you have on the Bluetooth keyboard and press RETURN and then back in 'bluetooth command shell'

# connect <MACADDRESS>

# -- You might have to reenter the connect, trust and pair commands and you may have to start from the begining
# -- To exit type:

# exit



# You may need to install these Python dependencies:
# sudo pip3 install evdev
# sudo pip3 install explorerhat


# Note: This script uses the first keyboard found, which could be USB or Bluetooth.
# So either only have the (bluetooth) keyboard you want connected or adjust KEYBOARD_INDEX, e.g. 1, 2, 3 ...
KEYBOARD_INDEX = 0

# Load library functions we want
from sys import exit
import atexit
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
    device = None
    if len(devices) > 0:
        device = devices[keyboard_index]

    return device



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


def end():
    exit(0)


# Run this whenever the script exits
@atexit.register
def cleanup():
    # disable all motors
    motor.stop()
    print("Bye")


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

    # Other commands
    ecodes.KEY_ESC: end,
}


try:
    print('Press ESCAPE or CTRL+C to quit')
    keyboard = get_keyboard(KEYBOARD_INDEX)

    if keyboard:
        for event in keyboard.read_loop():
            if event.type == ecodes.EV_KEY and event.code in keypress_actions:
                if event.value == 1:  # key down
                    keypress_actions[event.code]()
                if event.value == 0:  # key up
                    stop()
    else:
        print("No keyboard found!")

except KeyboardInterrupt:
    # CTRL+C exit
    print("stopping...")
