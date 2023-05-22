# UNI-T UT61E Python Library

Python library for reading data from UNI-T UT61E DMM.

## Update 12.2.2019. Added support to parse data you already have

If you have raw data from your UT61E using Arduino or some other µP, check ut61e_parser_example.py file in src folder to see how it works.

## Overview

This library was written as a weekend project. Its main goal was to learn the UNI-T UT61E data protocol.

## Connecting to UT61E

The project uses the IR RS-232 adapter which is supplied with the DMM and Python ```pyserial``` library to read the data.

Serial port settings are 19200bps, 7 data bits, odd parity, 1 stop bit. The supplied adapter also requires DTR=1 and RTS=0.

## UNI-T UT61E protocol

The DMM uses Cyrustek ES51922 chipset which is also used in other digital multimeters. My main source of information about its protocol was the [UT61E data log in DMM.exe project by Henrik Haftmann](https://www-user.tu-chemnitz.de/~heha/hs/UNI-T/UT61E.LOG).

Cyrustek ES51922 chipset has more features than are implemented in this project. This program implements only the features used by UT61E.

Each data packet contains 14 bytes.

```
Byte	Meaning
====	=======
0x00	Measurement range
        bit 6-3: always 0110
        bit 2-0: measurement range. See byte 6 for details.

0x01	Digit 1
        bit 6-4: always 011
        bit 3-0
			0000: 0
			0001: 1
			0010: 2
			0011: 3
			0100: 4
			0101: 5
			0110: 6
			0111: 7
			1000: 8
			1001: 9

0x02	Digit 2
        bit 6-4: always 011
        bit 3-0: See byte 0x01

0x03	Digit 3
        bit 6-4: always 011
        bit 3-0: See byte 0x01

0x04	Digit 4
        bit 6-4: always 011
        bit 3-0: See byte 0x01

0x05	Digit 5
        bit 6-4: always 011
        bit 3-0: See byte 0x01

0x06	DMM mode
        bit 6-4: always 011
        bit 3-0: Measurement mode
            Byte 6:  0xB       0x3       0x6       0x2       0xD       0xF       0x0      0x2
            Byte 0:  V, mV     Ohm       F         Hz        uA        mA        A        %
                0    2.2000    220.00    22.000n   220.00    220.00u   22.000m   10.000   100.0
                1    22.000    2.2000k   220.00n   2200.0    2200.0u   220.00m   -        100.0
                2    220.00    22.000k   2.2000u   -         -         -         -        -
                3    1000.0    220.00k   22.000u   22.000k   -         -         -        100.0
                4    220.00m   2.200M    220.00u   220.00k   -         -         -        100.0
                5    -         22.000M   2.2000m   2.2000M   -         -         -        100.0
                6    -         220.00M   22.000m   22.000M   -         -         -        100.0
                7    -         -         220.00m   220.00M   -         -         -        100.0

0x07	Info flags
        bit 6-4: always 011
        bit 3:   percent mode
        bit 2:   minus (negative value)
        bit 1:   low battery
        bit 0:   OL (overload)

0x08	Relative mode flags
        bit 6-4: always 011
        bit 3:   MAX (unused in this project)
        bit 2:   MIN (unused in this project)
        bit 1:   relative mode (delta)
        bit 0:   [RMR] (unused in this project)

0x09	Limit flags
        bit 6-4: always 011
        bit 3:   UL (underload)
        bit 2:   Peak max
        bit 1:   Peak min
        bit 0:   always 0

0x0A	Voltage and auto range flags
        bit 6-4: always 011
        bit 3:   DC measurement
        bit 2:   AC measurement
        bit 1:   auto range
        bit 0:   frequency measurement (Hz)
        
0x0B	Hold
        bit 6-4: always 011
        bit 3:   always 0
        bit 2:   VBAR (unused in this project)
        bit 1:   data hold
        bit 0:   LPF (unused in this project)

0x0C	Footer, always 0x0D (\r)
0x0D	Footer, always 0x0A (\n)

```

Each measurement value is encoded by 5 bytes which represent display digits.

## Program structure, settings and output data format

### UT61E() class

Class constructor requires serial port name only. all other settings are defined by the following constants.

```BAUD_RATE```, ```BITS```, ```PARITY```, ```STOP_BITS```: serial port settings (always 19200, 7 bits, odd parity, 1 stop bit).

```TIMEOUT```: serial port read timeout.

```EOL```: footer bytes of valid data packet. Always 0x0D 0x0D (CR, LF or \r\n).

```RAW_DATA_LENGTH```: data packet size.

```READ_RETRIES```: packet reading attempts. This value shows how many attempts to receive a valid packet should be made before returning an error.

The ```UT61E``` class contains the following functions:

```read_raw_data(self)```: reads raw data packet from serial port as array of byte values.

```is_data_valid(self, raw_data)```: returns ```True``` if the received packet is valid.

```read_hex_str_data(self)```: returns string with hexadecimal byte values of the received packet.

```get_meas(self)```: parses the received packet and returns the data as dicitonary (explained later).

```normalize_val(self, val, units)```:  normalizes the measured value to standard units (voltage to Volt, current to Ampere, resistance to Ohm, capacity to Farad, frequency to Herz, other values are not changed).

```pretty_print(self, disp_norm_val = False)```: prints the received measurement in human readable form.

### Returned data format

The received data is returned by ```get_meas()``` function as a dictionary with the following fields:

```mode``` [string]: measurement mode,

```range``` [string]: measurement range,

```val``` [float]: displayed value,

```units``` [string]: displayed units,

```norm_val``` [float]: displayed value, normalized to standard units (Volt, Ampere, Ohm, Farad, Herz),

```norm_units``` [string]: units of normalized value,

```percent``` [boolean]: duty cycle (%) measurement,

```minus``` [boolean]: negative value is displayed,

```low_bat``` [boolean]: low battery indicator,

```ovl``` [boolean]: OL is displayed,

```delta``` [boolean]: relative measurement (delta),

```ul``` [boolean]: UL is displayed,

```max``` [boolean]: peak max value,

```min``` [boolean]: peak min value,

```dc``` [boolean]: DC voltage is measured,

```ac``` [boolean]: AC voltage is measured,

```auto``` [boolean]: auto range,

```hz``` [boolean]: frequency measurement,

```hold``` [boolean]: data hold active,

```data_valid``` [bool]: True if data in the dictionary is valid.

### ut61e_monitor.py

```PORT```: default serial port which will be used if it is not specified in command line.

```SLEEP_TIME```: time between reading measurements.

## Running the script

The ```ut61e_monitor.py``` script is run from command line using the following command:

```python ut61e_monitor.py [com_port_name]```

where ```[com_port_name]``` is the name of serial port where your IR receiver is connected. In Windows it will be ```COM1```, ```COM2``` or another COM port. In Linux the will usually be ```/dev/ttyUSB0```, ```/dev/ttyUSB1``` etc. If not specified, the script will use port name stored in ```PORT``` constant.

## Output examples

![Output examples](https://raw.githubusercontent.com/4x1md/ut61e_py/master/images/output_example.png)

## Links

1. [DMM.exe project by Henrik Haftmann](https://www-user.tu-chemnitz.de/~heha/hs/UNI-T/)
2. [UT61E data log by Henrik Haftmann](https://www-user.tu-chemnitz.de/~heha/hs/UNI-T/UT61E.LOG)
3. [UNI-T UT61E schematic](http://www.frankshospitalworkshop.com/electronics/projects/voltage_reference/Uni-t%20UT61E.jpg)
4. [Multimeter ICs/Cyrustek ES519xx in sigrok Wiki](https://sigrok.org/wiki/Multimeter_ICs/Cyrustek_ES519xx)
5. [UT61E Protocol Description in GuShH's DevBlog](http://gushh.net/blog/ut61e-protocol/)
7. [Cyrustek ES51922 datasheet](http://www.cyrustek.com.tw/spec/ES51922.pdf)
6. [Uni-T UT60E RS-232 Data Logging](http://perfec.to/ut60e/)

## Questions? Suggestions?
You are more than welcome to contact me with any questions, suggestions or propositions regarding this project. You can:

1. Visit [my QRZ.COM page](https://www.qrz.com/db/4X1MD)
2. Visit [my Facebook profile](https://www.facebook.com/Dima.Meln)
3. Write me an email to iosaaris =at= gmail dot com

## How to Support or Say Thanks

If you like this project, or found here some useful information and want to say thanks, or encourage me to do more, you can buy me a coffee!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q4ITR7J)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/4x1md)

You can aslo make a donation with PayPal:

[!["Donate with PayPal"](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=NZZWZFH5ZBCCU)

---

**73 de 4X1MD**
