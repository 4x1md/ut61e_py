"""
Created on Sep 22, 2017

@author: Dmitry Melnichansky 4X1MD ex 4X5DM, 4Z7DTF
         https://github.com/4x1md
         http://www.qrz.com/db/4X1MD
         
@note: UT61E class which reads data packets from UNI-T UT61E using serial
       interface, parses them and returns as dictionary or as string in
       human readable form.
"""

import serial

# Settings constants
BAUD_RATE = 19200
BITS = serial.SEVENBITS
PARITY = serial.PARITY_ODD
STOP_BITS = serial.STOPBITS_ONE
DTR = True
RTS = False
TIMEOUT = 1
# Data packet ends with CR LF (\r \n) characters
EOL = b'\x0D\x0A'
RAW_DATA_LENGTH = 14
READ_RETRIES = 3

# UT61E protocol constants
# Significant bits in digit bytes
DIGIT_MASK = 0b00001111
# Bytes containing digits
DIGIT_BYTES = (1, 2, 3, 4, 5)

# Percent
# Byte 7 bit 3
PERCENT = 0b00001000

# Minus
# Byte 7 bit 2
NEG = 0b00000100

# Low battery
# Byte 7 bit 1
LOW_BAT = 0b00000010

# OL
# Byte 7 bit 0
OL = 0b00000001

# Relative mode
# Byte 8 bit 1
DELTA = 0b00000010

# UL
# Byte 9 bit 3
UL = 0b00001000

# MAX
# Byte 9 bit 2
MAX = 0b00000100

# MIN
# Byte 9 bit 1
MIN = 0b00000010

# DC
# Byte 10 bit 3
DC = 0b00001000

# AC
# Byte 10 bit 2
AC = 0b00000100

# AUTO
# Byte 10 bit 1
AUTO = 0b00000010

# Hz
# Byte 10 bit 0
HZ = 0b00000001

# Hold
# Byte 11 bit 1
HOLD = 0b00000010


# Measurement ranges
"""
Byte 6:  B         3         6         2         D         F         0        2
Byte 0:  V, mV     Ohm       F         Hz        uA        mA        A        %
    0    2.2000    220.00    22.000n   220.00    220.00u   22.000m   10.000   100.0
    1    22.000    2.2000k   220.00n   2200.0    2200.0u   220.00m   -        100.0
    2    220.00    22.000k   2.2000u   -         -         -         -        -
    3    1000.0    220.00k   22.000u   22.000k   -         -         -        100.0
    4    220.00m   2.200M    220.00u   220.00k   -         -         -        100.0
    5    -         22.000M   2.2000m   2.2000M   -         -         -        100.0
    6    -         220.00M   22.000m   22.000M   -         -         -        100.0
    7    -         -         220.00m   220.00M   -         -         -        100.0
"""

RANGE_V = (
    ('2.2000', 'V', 0.0001),
    ('22.000', 'V', 0.001),
    ('220.00', 'V', 0.01),
    ('1000.0', 'V', 0.1),
    ('220.00', 'mV', 0.01),
    )

RANGE_R = (
    ('220.00', 'Ohm', 0.01),
    ('2.2000', 'kOhm', 0.0001),
    ('22.000', 'kOhm', 0.001),
    ('220.00', 'kOhm', 0.01),
    ('2.2000', 'MOhm', 0.0001),
    ('22.000', 'MOhm', 0.001),
    ('220.00', 'MOhm', 0.01),
    )

RANGE_C = (
    ('22.000', 'nF', 0.001),
    ('220.00', 'nF', 0.01),
    ('2.2000', 'uF', 0.0001),
    ('22.000', 'uF', 0.001),
    ('220.00', 'uF', 0.01),
    ('2.2000', 'mF', 0.0001),
    ('22.000', 'mF', 0.001),
    ('220.00', 'mF', 0.01),
    )

RANGE_F = (
    ('220.00', 'Hz', 0.01),
    ('2200.0', 'Hz', 0.1),
    None,
    ('22.000', 'kHz', 0.001),
    ('220.00', 'kHz', 0.01),
    ('2.2000', 'MHz', 0.0001),
    ('22.000', 'MHz', 0.001),
    ('220.00', 'MHz', 0.01),
    )

RANGE_I_UA = (
    ('220.00', 'uA', 0.01),
    ('2200.0', 'uA', 0.1),
    )

RANGE_I_MA = (
    ('22.000', 'mA', 0.001),
    ('220.00', 'mA', 0.01),
    )

RANGE_I_A = (
    ('10.000', 'A', 0.001),
    )

RANGE_PERCENT = (
    ('100.0', '%', 0.01),
    ('100.0', '%', 0.01),
    None,
    ('100.0', '%', 0.01),
    ('100.0', '%', 0.01),
    ('100.0', '%', 0.01),
    ('100.0', '%', 0.01),
    )

# Measurement type
"""
0x00   A
0x01   Diode
0x02   Hz, %
0x03   Ohm
0x04   Temperature
0x05   Buzzer
0x06   F
0x07   A
0x0B   V, mV
0x0D   uA
0x0E   ADP
0x0F   mA
"""

MEAS_TYPE = (
    ('A', RANGE_I_A),
    ('Diode', RANGE_V),
    ('Hz/%', RANGE_F),
    ('Ohm', RANGE_R),
    ('deg', None),
    ('Buzzer', RANGE_R),
    ('Cap', RANGE_C),
    None,
    None,
    ('A', RANGE_I_A),
    None,
    ('V/mV', RANGE_V),
    None,
    ('uA', RANGE_I_UA),
    ('ADP', None),
    ('mA', RANGE_I_MA),
    )

# Normalization constants
# Each value contains multiplier and target value
NORM_RULES = {
    # Voltage
    'V':    (1, 'V'),
    'mV':   (1E-03, 'V'),
    # Current
    'A':    (1, 'A'),
    'mA':   (1E-03, 'A'),
    'uA':   (1E-06, 'A'),
    # Resistance
    'Ohm':  (1, 'Ohm'),
    'kOhm': (1E03, 'Ohm'),
    'MOhm': (1E06, 'Ohm'),
    # Capacitance
    'nF':   (1E-9, 'F'),
    'uF':   (1E-6, 'F'),
    'mF':   (1E-3, 'F'),
    # Frequency
    'Hz':   (1, 'Hz'),
    'kHz':  (1E03, 'Hz'),
    'MHz':  (1E06, 'Hz'),
    # Percent
    '%':    (1, '%'),
    }

# Output format
MEAS_RES = {
    # Mode and range
    'mode': None,
    'range': None,
    
    # Displayed value
    'val': None,
    'units': None,
    'norm_val': None,
    'norm_units': None,
    
    # Flags
    'percent': False,
    'minus': False,
    'low_bat': False,
    'ovl': False,
    'delta': False,
    'ul': False,
    'max': False,
    'min': False,
    'dc': False,
    'ac': False,
    'auto': False,
    'hz': False,
    'hold': False,
    
    'data_valid': False
    }


class UT61E(object):
    
    def __init__(self, port):
        self._port = port
        self._ser = serial.Serial(self._port, BAUD_RATE, BITS, PARITY, STOP_BITS, timeout=TIMEOUT)
        self._ser.setDTR(DTR)
        self._ser.setRTS(RTS)

    def read_raw_data(self):
        """Reads a new data packet from serial port.
        If the packet was valid returns array of integers.
        if the packet was not valid returns empty array.
        
        In order to get the last reading the input buffer is flushed
        before reading any data.
        
        If the first received packet contains less than 14 bytes, it is
        not complete and the reading is done again. Maximum number of
        retries is defined by READ_RETRIES value.
        """
        self._ser.reset_input_buffer()
        for x in range(READ_RETRIES):
            raw_data = self._ser.read_until(EOL, RAW_DATA_LENGTH)
            # If 14 bytes were read, the packet is valid and the loop ends.
            if len(raw_data) == RAW_DATA_LENGTH:
                break

        res = []
        
        # Check data validity
        if self.is_data_valid(raw_data):
            res = [ord(c) for c in bytes(raw_data).decode()]
        
        return res

    def is_data_valid(self, raw_data):
        """Checks data validity:
        1. 14 bytes long
        2. Footer bytes 0x0D 0x0A"""
        # Data length
        if len(raw_data) != RAW_DATA_LENGTH:
            return False
        
        # End bytes
        if not raw_data.endswith(EOL):
            return False
        
        return True
    
    def read_hex_str_data(self):
        """Returns raw data represented as string with hexadecimal values."""
        data = self.read_raw_data()
        codes = ["%02X" % c for c in data]
        return " ".join(codes)
    
    def get_meas(self):
        """Returns received measurement as dictionary"""
        res = MEAS_RES.copy()
        
        raw_data = self.read_raw_data()
        
        # If raw data is empty, return
        if len(raw_data) == 0:
            res['data_valid'] = False
            return res

        # Percent
        res['percent'] = True if raw_data[7] & PERCENT else False
        
        # Minus
        minus = True if raw_data[7] & NEG else False
        res['minus'] = minus
        
        # Low battery
        res['low_bat'] = True if raw_data[7] & PERCENT else False
        
        # Overload
        res['ovl'] = True if raw_data[7] & OL else False
        
        # Delta
        res['delta'] = True if raw_data[8] & DELTA else False
        
        # UL
        res['ul'] = True if raw_data[9] & UL else False
        
        # MAX
        res['max'] = True if raw_data[9] & MAX else False
        
        # MIN
        res['min'] = True if raw_data[9] & MIN else False
        
        # DC
        res['dc'] = True if raw_data[10] & DC else False
        
        # AC
        res['ac'] = True if raw_data[10] & AC else False
        
        # AUTO
        res['auto'] = True if raw_data[10] & AUTO else False
        
        # Herz
        res['hz'] = True if raw_data[10] & HZ else False
        
        # Hold
        res['hold'] = True if raw_data[11] & HOLD else False
        
        # Measurement mode, range and units
        meas_type = MEAS_TYPE[raw_data[6] & 0x0F]
        range_id = raw_data[0] & 0b00000111
        # If Herz or % is chosen in voltage or current measurement
        # mode, corresponding range tuple is chosen.
        if res['percent']:
            meas_range = RANGE_PERCENT[range_id]
        elif res['hz']:
            meas_range = RANGE_F[range_id]
        else:
            meas_range = meas_type[1][range_id]
        res['mode'] = meas_type[0]
        res['range'] = meas_range[0]
        res['units'] = meas_range[1]
        multiplier = meas_range[2]
        
        # Value
        val = 0
        for n in DIGIT_BYTES:
            digit = raw_data[n] & DIGIT_MASK
            val = val * 10 + digit
        val *= multiplier
        val = -val if minus else val
        res['val'] = val
        
        # Normalize value
        nval = self.normalize_val(res['val'], res['units'])
        res['norm_val'] = nval[0]
        res['norm_units'] = nval[1]
        
        res['data_valid'] = True
        
        return res
    
    def normalize_val(self, val, units):
        """Normalizes measured value to standard units. Voltage 
        is normalized to Volt, current to Ampere, resistance to Ohm,
        capacitance to Farad and frequency to Herz.
        Other units are not changed."""
        val = val * NORM_RULES[units][0]
        units = NORM_RULES[units][1]
        return (val, units) 

    def get_readable(self, disp_norm_val=False):
        """Prints measurement details in human readable form.
        disp_norm_val: if True, normalized values will also be displayed.
        """
        data = self.get_meas()
        
        if not data.get('data_valid', False):
            return "UT61E is not connected."
        
        res = ""
        
        # AC/DC, HOLD, REL and low battery
        ac_dc = ''
        if data['dc']:
            ac_dc = 'DC'
        elif data['ac']:
            ac_dc = 'AC'
        peak = ''
        if data['min']:
            peak = 'MIN'
        elif data['max']:
            peak = 'MAX'
        hold = 'HOLD' if data['hold'] else ''
        rel = 'REL' if data['delta'] else ''
        low_bat = 'LOW BAT' if data['low_bat'] else ''
        res += "%s\t%s\t%s\t%s\t%s\n" % (ac_dc, peak, hold, rel, low_bat)
        
        # Mode and range
        if data['auto']:
            res += "MODE: %s\tAUTO\n" % (data['mode'])
        else:
            res += "MODE: %s\t%s %s\n" % (data['mode'], data['range'], data['units'])
        
        # Displayed value        
        if data['ovl']:
            res += "OL\n"
        elif data['ul']:
            res += "UL\n"
        else:
            res += "%s %s\n" % (data['val'], data['units'])

        # Display normalized values
        # If the DMM displayes OL or UL these values will be displayed
        if disp_norm_val:
            if data['ovl']:
                res += "OL"
            elif data['ul']:
                res += "UL"
            else:
                res += "= %s %s" % (data['norm_val'], data['norm_units'])
        
        return res
    
    def __del__(self):
        if hasattr(self, '_ser'):
            self._ser.close()

if __name__ == '__main__':
    pass
