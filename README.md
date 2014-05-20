Peachy Printer Tools
==================

Status
-------------------------

Very Active Development (BETA - 2)


Known Issues
--------------------------

+ Audio settings show despite a lack of support for sound card. http://stackoverflow.com/questions/23553470/pyaudio-supports-all-formats-despite-the-fact-the-audio-card-does-not
+ Drip detection may require audio boost on some systems.
+ Models pre PP29 may drive mirrors too far to calibrate properly
+ Poor context sensitive help.



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

Please be aware that by contributing you agree to assignment of your copyrite to Peachy Printer LLC. We do this for logistics and managment we will respect you freedoms and keep this source open.

Need help contributing? Please check out the forums: http://forum.peachyprinter.com/


Licence
---------------------------

Please see the LICENSE file


Development 
--------------------------
#### Dependancies

+ python 2.7
+ numpy
+ cx_freeze
+ pyaudio
+ mock
+ pyserial


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
