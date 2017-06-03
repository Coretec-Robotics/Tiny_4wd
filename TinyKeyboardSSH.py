#!/usr/bin/env python
# coding: Latin-1
# Load library functions we want
from sys import exit
import atexit
import curses
from explorerhat import motor

# --------------------------------------------------------------------------------------------------------
# Info

# Purpose: Control a Tiny4WD using keyboard keys within a ssh-session
# Editor : Stefan Theurer sttheurer@googlemail.com
# Thanks for the well written recipe on
# https://gpiozero.readthedocs.io/en/stable/recipes.html#keyboard-controlled-robot

# ------------------------------------------------------------------------------------------
# Python Libraries

# You may need to install these Python dependencies:

# sudo pip3 install explorerhat



# The max speed setting for the motors.
MAX_SPEED=100

# Depending on which way round the positive and negative wires are connected to the motors,
# one or both of these values may need to be negative, e.g. -MAX_POWER
LEFT_MOTOR_MAX_SPEED_FWD  = MAX_SPEED       # The top speed that makes the left motors turn in the forward direction
RIGHT_MOTOR_MAX_SPEED_FWD = -MAX_SPEED       # The top speed that makes the right motors turn in the forward direction

# Depending on which side of your robot motors are mounted these might need swapping
left_motor = motor.two                      # The explorer pHAT 'motor.one' is connected to the robots left hand motors
right_motor = motor.one                     # The explorer pHAT 'motor.two' is connected to the robots right hand motors


# --------------------------------------------------------------------------------------------------------
# Utilities

# Run this whenever the script exits
@atexit.register
def cleanup():
    # disable all motors
    motor.stop()
    print("Bye")


# --------------------------------------------------------------------------------------------------------
# Motor Control

# You shouldn't need to change these, but if the robot is not going in the direction you expect
# please see the settings section above and adjust the LEFT_MOTOR_MAX_POWER_FWD, RIGHT_MOTOR_MAX_POWER_FWD
# left_motor & right_motor settings there.

def forward():
    left_motor.speed(LEFT_MOTOR_MAX_SPEED_FWD)
    right_motor.speed(RIGHT_MOTOR_MAX_SPEED_FWD)

def backward():
    left_motor.speed(-LEFT_MOTOR_MAX_SPEED_FWD)
    right_motor.speed(-RIGHT_MOTOR_MAX_SPEED_FWD)

def left():
    left_motor.speed(-LEFT_MOTOR_MAX_SPEED_FWD)
    right_motor.speed(RIGHT_MOTOR_MAX_SPEED_FWD)

def right():
    left_motor.speed(LEFT_MOTOR_MAX_SPEED_FWD)
    right_motor.speed(-RIGHT_MOTOR_MAX_SPEED_FWD)

def stop():
    left_motor.speed(0)
    right_motor.speed(0)


def end():
    exit(0)

# --------------------------------------------------------------------------------------------------------
# Keyboard Actions

actions = {
    # Arrow keys:
    curses.KEY_UP:   forward,
    curses.KEY_DOWN:  backward,
    curses.KEY_LEFT:  left,
    curses.KEY_RIGHT: right,
    }

# --------------------------------------------------------------------------------------------------------
# Main

def main(window):
    next_key = None

    while True:
        if next_key is None:
            key = window.getch()
        else:
            key = next_key
            next_key = None
        if key != -1:
            # KEY DOWN
            curses.halfdelay(1)
            action = actions.get(key)
            if action is not None:
                action()
            next_key = key
            while next_key == key:
                next_key = window.getch()
            # KEY UP
            stop()

curses.wrapper(main)
