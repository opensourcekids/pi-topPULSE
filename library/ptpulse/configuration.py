# configuration.py (pi-topPULSE)
# Copyright (C) 2017  CEED ltd.
#

from math import pow
import smbus
import sys
import time
from numpy import uint8

_bus_id = 1
_device_addr = 0x24
_debug = False

_speaker_bit = 0
_mcu_bit = 1
_eeprom_bit = 2
_16khz_bit = 3

#######################
# INTERNAL OPERATIONS #
#######################

def _debug_print(message):
    """INTERNAL. Print messages if debug mode enabled."""

    if _debug == True:
        print(message)  


def _get_addr_for_bit(bit):
    if bit in [0,1,2,3]:
        _debug_print("bit:  " + str(bit))
        addr = uint8(pow(2, bit))
        _debug_print("addr: " + str(addr))
        return addr
    else:
        print("Internal ERROR: invalid bit; cannot get address")
        sys.exit()


def _get_bit_string(value):
    """INTERNAL. Get string representation of an int in binary"""

    return "{0:b}".format(value).zfill(8)


def _update_device_state_bit(bit, value):
    """INTERNAL. Set a particular device state bit to enable or disable a particular function"""

    # Bits:  0x0000
    # Index:   3210

    if bit not in [0,1,2,3]:
        print("Error: Not a valid state bit")
        return False

    try:
        current_state = _read_device_state()
        _debug_print("Current device state: " + _get_bit_string(current_state))

    except:
        print("Error: There was a problem getting the current device state")
        return False

    # Get the bit mask for the new state
    new_state = _get_addr_for_bit(bit)

    if value == 0:
        new_state = ~new_state

    # Check if there is anything to do
    if (value == 1 and (new_state & current_state) != 0) or (value == 0 and (~new_state & ~current_state) != 0):
        _debug_print("Warning: Mode already set, nothing to send")
        return True

    if value == 0:
        new_state = new_state & current_state
    else:
        new_state = new_state | current_state

    # Combine the old with the new and send
    return _write_device_state(new_state)


def _verify_device_state(expected_state):
    """INTERNAL. Verify that that current device state matches that expected"""

    current_state = _read_device_state()

    if expected_state == current_state:
        return True

    else:
        print("Error: Device write verification failed. Expected: " + _get_bit_string(expected_state) + " Received: " + _get_bit_string(current_state))
        return False


def _write_device_state(state): 
    """INTERNAL. Send the state bits across the I2C bus"""

    try:
        _debug_print("Connecting to bus...")
        i2c_bus = smbus.SMBus(_bus_id)

        state_to_send = 0x0F & state

        _debug_print("Writing new state:    " + _get_bit_string(state_to_send))
        i2c_bus.write_byte_data(_device_addr, 0, state_to_send)

        result = _verify_device_state(state_to_send)

        if result == True:
            _debug_print("OK")
        else:
            print("Error: New state could not be verified")

        return result

    except:
        print("Error: There was a problem writing to the device")
        return False


def _read_device_state():
    """INTERNAL. Read from the I2C bus to get the current state of the pulse. Caller should handle exceptions"""
    
    try:
        _debug_print("Connecting to bus...")
        i2c_bus = smbus.SMBus(_bus_id)

        current_state = i2c_bus.read_byte(_device_addr) & 0x0F

        return uint8(current_state)

    except:
        print("Error: There was a problem reading from the device")
        # Best to re-raise as we can't recover from this
        raise


#######################
# EXTERNAL OPERATIONS #
#######################

# SET STATE

def set_debug_print_state(debug_enable):
    """Enable/disable debug prints"""

    global _debug
    _debug = debug_enable

def reset_device_state(enable):
    """Reset the device state bits to the default enabled or disabled state"""

    clean_enable_state = _get_addr_for_bit(_eeprom_bit)
    clean_disable_state = _get_addr_for_bit(_speaker_bit) | _get_addr_for_bit(_mcu_bit)

    state_to_send = clean_enable_state if enable else clean_disable_state
    return _write_device_state(state_to_send)


def set_microphone_sample_rate_to_16khz():
    """Set the appropriate I2C bits to enable 16,000Hz recording on the microphone"""

    return _update_device_state_bit(_16khz_bit, 1)


def set_microphone_sample_rate_to_22khz():
    """Set the appropriate I2C bits to enable 22,050Hz recording on the microphone"""

    return _update_device_state_bit(_16khz_bit, 0)


# GET STATE

def speaker_enabled():
    """Get whether the speaker is enabled"""
    
    return (_read_device_state() & _get_addr_for_bit(_speaker_bit)) == 0


def mcu_enabled():
    """Get whether the onboard MCU is enabled"""

    return (_read_device_state() & _get_addr_for_bit(_mcu_bit)) == 0


def eeprom_enabled():
    """Get whether the eeprom is enabled"""

    return (_read_device_state() & _get_addr_for_bit(_eeprom_bit)) != 0


def microphone_sample_rate_is_16khz():
    """Get whether the microphone is set to record at a sample rate of 16,000Hz"""

    return (_read_device_state() & _get_addr_for_bit(_16khz_bit)) != 0


def microphone_sample_rate_is_22khz():
    """Get whether the microphone is set to record at a sample rate of 22,050Hz"""

    return (_read_device_state() & _get_addr_for_bit(_16khz_bit)) == 0
