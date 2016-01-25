Peachy Printer Tools
==================

Status
-------------------------

Active Development as of 25-Jan-2016

Note
---------------------------
This is an API only to run the full suite of peachy printer use peachyprinter at https://github.com/PeachyPrinter/peachyprinter


Known Issues
--------------------------

Calibration can be poor in some circumstances
Low level error are not raised properly

Support
--------------------------

All support for Peachy Printer Tools located at http://forum.peachyprinter.com/


Contributing 
--------------------------

Yes please. 

Peachy Printer and it software are community driven, Please send us a pull request.

In order to be considered please ensure that:
+ Test Driven Design (TDD) write your tests first then write the code to make them work.
+ Respect the Single Responsibility Principal
+ Follow Onion Archetecture Principals
+ PEP8 formatting [Excpeting line length(E501) we are not programming on terminals anymore]

Please be aware that by contributing you agree to assignment of your copyrite to Peachy Printer INC. We do this for logistics and managment we will respect you freedoms and keep this source open.

Need help contributing? Please check out the forums: http://forum.peachyprinter.com/


Licence
---------------------------

Please see the LICENSE file


Development 
--------------------------
#### Dependancies

+ python 2.7
+ numpy
+ mock (development only)
+ pyserial
+ python protobuf
+ protobuf
+ libusb1

##### Windows
c++ compiler for python http://www.microsoft.com/en-us/download/details.aspx?id=44266


#### Runing the tests

Run Suite Once

**python test/test-all.py**

Run Suite on Every Change (linux like OS only )

**./runsuite test/test-all.py**




Software Contributers
--------------------------

+ James Townley (Lead)
+ https://github.com/Pete5746218
