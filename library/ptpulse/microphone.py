# microphone.py (pi-topPULSE) 
# Copyright (C) 2017  CEED ltd.
#

import codecs
import binascii
import math
from tempfile import mkstemp
import os
import serial
import signal
import struct
import sys
from threading import Thread
import time
# local
from ptpulse import configuration

_debug = False
_bitrate = 8
_continue_writing = False
_recording_thread = False
_thread_running = False
_exiting = False
_temp_file_path = ""

#######################
# INTERNAL OPERATIONS #
#######################

def _debug_print(message):
    """INTERNAL. Print messages if debug mode enabled."""

    if _debug == True:
        print(message)  


def _signal_handler(signal, frame):
    """INTERNAL. Handles signals from the OS."""

    global _exiting

    if _exiting == False:
        _exiting = True

        if _thread_running == True:
            stop()
    
    print("\nQuitting...")
    sys.exit(0)
    

def _get_size(filename):
    """INTERNAL. Gets the size of a file."""

    file_stats = os.stat(filename)
    return file_stats.st_size


def _from_hex(value):
    """INTERNAL. Gets a bytearray from hex data."""

    return bytearray.fromhex(value)


def _space_separated_little_endian(integer_value, byte_len):
    """INTERNAL. Get an integer in format for WAV file header."""
    
    if byte_len <= 1:
        pack_type = '<B'
    elif byte_len <= 2:
        pack_type = '<H'
    elif byte_len <= 4:
        pack_type = '<I'
    elif byte_len <= 8:
        pack_type = '<Q'
    else:
        print("Value cannot be represented in 8 bytes - exiting")
        sys.exit()

    hex_string = struct.pack(pack_type, integer_value)
    temp = binascii.hexlify(hex_string).decode()
    return ' '.join([temp[i:i+2] for i in range(0, len(temp), 2)])


def _init_header_information():
    """INTERNAL. Create a WAV file header."""

    RIFF = "52 49 46 46"
    WAVE = "57 41 56 45"
    fmt  = "66 6d 74 20"
    DATA = "64 61 74 61"

    if configuration.microphone_sample_rate_is_22khz():
        capture_sample_rate = 22050
    else:
        capture_sample_rate = 16000

    header =  _from_hex(RIFF)                                                   # ChunkID
    header += _from_hex(_space_separated_little_endian(0, 4))        			# ChunkSize - 4 bytes (to be changed depending on length of data...)
    header += _from_hex(WAVE)                                                   # Format
    header += _from_hex(fmt)                                                    # Subchunk1ID
    header += _from_hex(_space_separated_little_endian(16, 4))       			# Subchunk1Size (PCM = 16)
    header += _from_hex(_space_separated_little_endian(1, 2))        			# AudioFormat   (PCM = 1)
    header += _from_hex(_space_separated_little_endian(1, 2))        			# NumChannels
    header += _from_hex(_space_separated_little_endian(capture_sample_rate, 4)) # SampleRate
    header += _from_hex(_space_separated_little_endian(capture_sample_rate, 4)) # ByteRate (Same as SampleRate due to 1 channel, 1 byte per sample)
    header += _from_hex(_space_separated_little_endian(1, 2))        			# BlockAlign - (no. of bytes per sample)
    header += _from_hex(_space_separated_little_endian(_bitrate, 2)) 			# BitsPerSample
    header += _from_hex(DATA)                                                   # Subchunk2ID
    header += _from_hex(_space_separated_little_endian(0, 4))        			# Subchunk2Size - 4 bytes (to be changed depending on length of data...)

    return header


def _update_header_in_file(file, position, value):
    """INTERNAL. Update the WAV header  """

    hex_value = _space_separated_little_endian(value, 4)
    data = binascii.unhexlify(''.join(hex_value.split()))
    
    file.seek(position)
    file.write(data)


def _finalise_wav_file(file_path):
    """INTERNAL. Update the WAV file header with the size of the data."""

    size_of_data = _get_size(file_path) - 44

    if size_of_data <= 0:
        print("Error: No data was recorded!")
        os.remove(file_path)
    else:
        with open(file_path, 'rb+') as file:

            _debug_print("Updating header information...")

            _update_header_in_file(file, 4, size_of_data + 36)
            _update_header_in_file(file, 40, size_of_data)


def _thread_method():
    """INTERNAL. Thread method."""

    _record_audio()


def _record_audio():
    """INTERNAL. Open the serial port and capture audio data into a temp file."""

    global _temp_file_path

    temp_file_tuple = mkstemp()
    os.close(temp_file_tuple[0])
    _temp_file_path = temp_file_tuple[1]

    if os.path.exists('/dev/serial0'):      

        _debug_print("Opening serial device...")

        serial_device = serial.Serial(port = '/dev/serial0', timeout = 1, baudrate = 250000, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS)
        serial_device_open = serial_device.isOpen()

        if serial_device_open == True:
            
            try:
                _debug_print("Start recording")
                
                with open(_temp_file_path, 'wb') as file:

                    _debug_print("WRITING: initial header information")
                    file.write(_init_header_information())

                    if serial_device.inWaiting():
                        _debug_print("Flushing input and starting from scratch")
                        serial_device.flushInput()

                    _debug_print("WRITING: wave data")

                    while _continue_writing:
                        while not serial_device.inWaiting():
                            time.sleep(0.01)
                        
                        audio_output = serial_device.read(serial_device.inWaiting())
                        data_to_write = ""
                        bytes_to_write = bytearray()

                        for pcm_data_block in audio_output:

                            if _bitrate == 16:

                                pcm_data_int = 0
                                if sys.version_info >= (3, 0):
                                    pcm_data_int = pcm_data_block
                                    scaled_val = int((pcm_data_int * 32768) / 255)
                                    bytes_to_write += _from_hex(_space_separated_little_endian(scaled_val, 2))

                                else:
                                    pcm_data_int = ord(pcm_data_block)
                                    scaled_val = int((pcm_data_int * 32768) / 255)
                                    data_to_write += _from_hex(_space_separated_little_endian(scaled_val, 2))
                                
                            else:

                                if sys.version_info >= (3, 0):
                                    pcm_data_int = pcm_data_block
                                    bytes_to_write += _from_hex(_space_separated_little_endian(pcm_data_int, 1))

                                else:
                                    pcm_data_int = ord(pcm_data_block)
                                    data_to_write += _from_hex(_space_separated_little_endian(pcm_data_int, 1))

                        if sys.version_info >= (3, 0):
                            file.write(bytes_to_write)
                        else:
                            file.write(data_to_write)
                        
                        time.sleep(0.1)

            finally:
                serial_device.close()

                _finalise_wav_file(_temp_file_path)

                _debug_print("Finished Recording.")

        else:
            print("Error: Serial port failed to open")

    else:
        print("Error: Could not find serial port - are you sure it's enabled?")


#######################
# EXTERNAL OPERATIONS #
#######################

def record():
    """Start recording on the pi-topPULSE microphone."""

    global _thread_running
    global _continue_writing
    global _recording_thread

    if not configuration.mcu_enabled():
        print("Error: pi-topPULSE is not initialised.")
        sys.exit()

    if _thread_running == False:
        _thread_running = True
        _continue_writing = True
        _recording_thread = Thread(group=None, target=_thread_method)
        _recording_thread.start()
    else:
        print("Microphone is already recording!")


def is_recording():
    """Returns recording state of the pi-topPULSE microphone."""

    return _thread_running


def stop():
    """Stops recording audio"""

    global _thread_running
    global _continue_writing

    _continue_writing = False
    _recording_thread.join()
    _thread_running = False
    

def save(file_path, overwrite=False):
    """Saves recorded audio to a file."""

    global _temp_file_path

    if _thread_running == False:
        if _temp_file_path != "" and os.path.exists(_temp_file_path):
            if os.path.exists(file_path) == False or overwrite == True:
                
                if os.path.exists(file_path):
                    os.remove(file_path)

                os.rename(_temp_file_path, file_path)
                _temp_file_path = ""

            else:
                print("File already exists")
        else:
            print("No recorded audio data found")
    else:
        print("Microphone is still recording!")


def set_sample_rate_to_16khz():
    """Set the appropriate I2C bits to enable 16,000Hz recording on the microphone"""

    configuration.set_microphone_sample_rate_to_16khz()


def set_sample_rate_to_22khz():
    """Set the appropriate I2C bits to enable 22,050Hz recording on the microphone"""

    configuration.set_microphone_sample_rate_to_22khz()


def set_bit_rate_to_unsigned_8():
    """Set bitrate to device default"""

    global _bitrate
    _bitrate = 8


def set_bit_rate_to_signed_16():
    """Set bitrate to double that of device default by scaling the signal"""

    global _bitrate
    _bitrate = 16


#######################
# INITIALISATION      #
#######################

_signal = signal.signal(signal.SIGINT, _signal_handler)
