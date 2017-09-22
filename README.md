# UNI-T UT61E Python Library

Python library for reading data from UNI-T UT61E DMM.

## Running the script

The ```ut61e_monitor.py``` script is run from command line using the following command:

```python ut61e_monitor.py [com_port_name]```

where ```[com_port_name]``` is the name of serial port where your IR receiver is connected. In Windows it will be ```COM1```, ```COM2``` or another COM port. In Linux the will usually be ```/dev/ttyUSB0```, ```/dev/ttyUSB1``` etc. If not specified, the script will use port name stored in ```PORT``` constant.

## Links

1. [DMM.exe project by Henrik Haftmann](https://www-user.tu-chemnitz.de/~heha/hs/UNI-T/)
2. [UT61E data log by Henrik Haftmann](https://www-user.tu-chemnitz.de/~heha/hs/UNI-T/UT61E.LOG)
3. [UNI-T UT61E schematic](http://www.frankshospitalworkshop.com/electronics/projects/voltage_reference/Uni-t%20UT61E.jpg)
4. [Multimeter ICs/Cyrustek ES519xx in sigrok Wiki](https://sigrok.org/wiki/Multimeter_ICs/Cyrustek_ES519xx)
5. [UT61E Protocol Description in GuShH's DevBlog](http://gushh.net/blog/ut61e-protocol/)

## Questions? Suggestions?
You are more than welcome to contact me with any questions, suggestions or propositions regarding this project. You can:

1. Visit [my QRZ.COM page](https://www.qrz.com/db/4X1MD)
2. Visit [my Facebook profile](https://www.facebook.com/Dima.Meln)
3. Write me an email to iosaaris =at= gmail dot com

73 de 4X1MD
