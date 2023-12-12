"""
Notes
- need to install cutie library (pip3 cutie)
- need to use python3 specifically (won't work for python2)

- to select commands:
- press the space bar to select (can select multiple at once)
- use arrow keys to move
- press enter to confirm
- to enter parameters: 
to execute $PQSETINSMSG,1,1,100*53s
give 1,1,100*53 when asked for parameters
"""

import sys
import cutie
import serial
import math
import time
import datetime
import pynmea2

# Execute command
def send_command(port, command, target):
    print('Executing ' + command + ' expecting ' + target)
    command = pynmea2.parse(command).render() + "\r\n"
    print(command)
    port.flushInput()
    port.write(command.encode())
    print('Executing command . . .')

    if target != 'no response message':
        log = []
        i, g = 0, 0
        while i < 500:
            i += 1
            line = port.readline().decode('utf-8', errors='ignore')
            log.append(line)
            print(line)
            if target in line:
                print('\nSuccess!\n' + line)
                break 

        else:
            print('Response message not found.')
            if cutie.prompt_yes_or_no('Would you like to print out the messages received?'):
                for g in log:
                    print(g)

    else:
        print('Response message not expected for this command.')

# Prompt the user for the COM port name
com_port = "/dev/ttyS0"
# Default to "COM10" if the user didn't provide one
com_port = com_port if com_port else "COM10"

# Setup serial
device = 'LC29H' # default
baud = 115200 # default
for arg in sys.argv: # set custom
        if ('29' in arg):
            device = 'LC29H'
        if ('460800' in arg):
            baud = 460800
        if ('921600' in arg):
            baud = 921600

ser = serial.Serial(com_port, baud, parity='N', bytesize=8, stopbits=1, timeout=None) # need to confirm the port
ser.flushInput()

while True:
    if ser.isOpen(): break

print('Port is open now\n')
ser.flushInput()

# Enter commands
while True:

    if device == 'LC29H':
        options = [
            'PQTMVERNO',
            'PQTMSAVEPAR',
            'PAIR_ACK',
            'PAIR_RTCM_SET_OUTPUT_MODE',
            'PAIR_RTCM_GET_OUTPUT_MODE',
            'PAIR_RTCM_SET_OUTPUT_EPHEMERIS',
            'EXIT'
        ]
    chosen = []


    selected = cutie.select_multiple(options,hide_confirm=True)
    for s in selected:
      chosen.append(options[s])

    for command in chosen: 
        if command == 'PQTMVERNO':
            target = '$PQTMVERNO'
        elif command == 'PAIR_ACK':
            commandID = input("Enter commandID parameter: ")
            result = input("Enter result parameter: ")
            command = command + ',' + commandID + result
            target = '$PAIR001'
        elif command == 'PAIR_RTCM_SET_OUTPUT_MODE':
            mode = input("Enter mode parameter: ")
            command = 'PAIR432' + ',' + mode
            target = '$PAIR001'
        elif command == 'PAIR_RTCM_GET_OUTPUT_MODE':
            command = 'PAIR433'
            target = '$PAIR001'
        elif command == 'PAIR_RTCM_SET_OUTPUT_EPHEMERIS':
            enable = input("Enter enable parameter: ")
            command = 'PAIR436' + ',' + enable
            target = '$PAIR001'
        elif command == 'EXIT':
            exit()

    response = send_command(ser, command, target)
