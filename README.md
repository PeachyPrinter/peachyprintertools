Peachy Printer Tools
==================

Status
-------------------------

Very Active Development (BETA - 2)


Known Issues
--------------------------

+ Drip detection may require audio boost on some systems.
+ Models pre PP29 may drive mirrors too far to calibrate properly


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
+ mock
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

#### Running the application 

Run the application

**python src/peachyprintertools.py**

Run in Debug Logging Mode

**python src/peachyprintertools.py --log=DEBUG**

Run in DEBUG to Console (Very slow)

**python src/peachyprintertools.py -c --log=DEBUG**

Log Levels:
+ DEBUG
+ INFO
+ WARN
+ ERROR

Logs and configs are stored in the user folder in the .peachyprintertools directory.


Software Contributers
--------------------------

+ James Townley (Lead)
+ https://github.com/Pete5746218
