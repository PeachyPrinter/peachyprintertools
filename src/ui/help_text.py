options_help = '''These are general settings for the Peachy Printer.  It is strongly recommended that if you change these values you re-calibrate the printer.\n
Spot Diameter (mm) [0.5] - <b>Sets</b> the current size of the laser beam, 0.5 is a good default for the Peachy Printer.\n
Sub Layer Height (mm) [0.05] - Sublayers are added to your model when the vertical resolution of the model is not fine enough. 0.05mm works out to about 600dpi.\n
Maximum Lead Distance (mm) [0.5] - If you are dripping too fast this is the distance ahead at which the printer will start skipping sublayers.'''

calibration_help = '''Description: Calibrating your printer will help account for discrepancies in centering, distance from the print area, and physical differences between each printer. This process is required every time you change the printer height, move the internal components of the printer (such as a hard bump or a fall), change computers, or change sound cards.\n

Process Overview:  The calibration process involves sending a series of audio signals to the Peachy Printer that make the laser beam move to 4 different positions.  Using the Calibration Grid as a reference, you must record the distance of these positions from the grid's center point on both the X and Y axises.  These values are then entered in the appropriate fields in the calibration software.  This process is done twice - at the print base level (0), and at the top of your print reservoir.  This allows the software to account for the reduction in laser deflection as the print surfaces rises on the Z-axis.  Once you've recorded and entered all of the real-world coordinates at both heights, you can then test out your calibrated printer by playing any of the signals offered in "Calibrated Patterns".\n

1. Place your calibration grid on top of your lower reservoir underneath the printer.\n

2. Using "Center Point" position the calibration grid so that the laser beam is in the center of the grid.\n

3. Using "Alignment" rotate the grid until the dark center gridline is aligned with the laser line.\n

4.  Go back to "Center Point" to ensure that the grid is still centered.  If it's not, continue going back and forth between "Center Point" and "Alignment" until the grid is positioned correctly.\n

5.  Using "Scale" ensure that the laser path will fall within the bounds of your lower reservoir.\n

Note: Scale is the percentage of the volume range of your sound card that the printer will use.  We highly recommend keeping it below 75% because to top 25% of sound cards ( the really loud sounds) don't come out quite right and that makes for very warped prints!\n

6.1.  In "Calibrate" enter the maximum print height for the reservoir you chose in the "Upper Calibration Height" field.\n

Note: The maximum print height is the distance between the print base level (the level at which you start a print) to the maximum height of your lower reservoir.  You calculate this by measuring the height of your wire mesh print base, and subtracting that from the height of your lower reservoir.  For example - 6 cm (height of lower reservoir) subtract 1 cm (height of print base) = 5 cm (maximum print height).\n

6.2.  Click inside the first set of "Actual X" and "Actual Y" values (either field will work). The laser beam should move to a new position on the calibration grid.  Measure (in mm) the X and Y coordinates of the laser beams position from the center lines on the grid and enter them in their respective fields.\n

6.3. Complete the upper height calibration by repeating step 6.2. for the remaining 3 sets of "Actual X" and "Actual Y" values.\n

7.  Remove your lower reservoir and place your calibration grid on top of your print base underneath the printer.\n

8.  Repeat steps 2-4 to ensure that your calibration grid is centered and aligned.\n

9.  Complete the lower height calibration by repeating the same process done in step 6.2. for the 4 sets of "Actual X" and "Actual Y" values.\n

10.  Click "Save".\n

11.  Replace the calibration grid with the glow paper square.  Play the signals in "Calibrated Patterns" to test out your calibrated Peachy Printer.
'''

setup_audio_help = '''Some help setting up audio goes here'''

setup_drip_calibration_help = '''Adjust the microphone input on your computer to make the drips count correctly.\n
enter the End Height that you will wait for the drips to get to.\n
When your drips get to your end height click mark. \n
Click save to save your chanages'''

cure_test_help = '''Help setting up and running a cure test goes here'''
