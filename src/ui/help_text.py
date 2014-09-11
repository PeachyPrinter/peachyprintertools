options_help = '''These are general settings for the Peachy Printer.  It is strongly recommended that if you change these values you re-calibrate the printer.

Spot Diameter (mm) [0.5] - <b>Sets</b> the current size of the laser beam, 0.5 is a good default for the Peachy Printer.

Sub Layer Height (mm) [0.05] - Sublayers are added to your model when the vertical resolution of the model is not fine enough. 0.05mm works out to about 600dpi.

Maximum Lead Distance (mm) [0.5] - If you are dripping too fast this is the distance ahead at which the printer will start skipping sublayers.'''

calibration_help = '''Description: Calibrating your printer will help account for discrepancies in centering, distance from the print area, and physical differences between each printer. This process is required every time you change the printer height, move the internal components of the printer (such as a hard bump or a fall), change computers, or change sound cards.

Process Overview:  The calibration process involves sending a series of audio signals to the Peachy Printer that make the laser beam move to 4 different positions.  Using the Calibration Grid as a reference, you must record the distance of these positions from the grid's center point on both the X and Y axises.  These values are then entered in the appropriate fields in the calibration software.  This process is done twice - at the print base level (0), and at the top of your print reservoir.  This allows the software to account for the reduction in laser deflection as the print surfaces rises on the Z-axis.  Once you`ve recorded and entered all of the real-world coordinates at both heights, you can then test out your calibrated printer by playing any of the signals offered in "Calibrated Patterns".

1. Place your calibration grid on top of your lower reservoir underneath the printer.

2. Using "Center Point" position the calibration grid so that the laser beam is in the center of the grid.

3. Using "Alignment" rotate the grid until the dark center gridline is aligned with the laser line.

4.  Go back to "Center Point" to ensure that the grid is still centered.  If it's not, continue going back and forth between "Center Point" and "Alignment" until the grid is positioned correctly.

5.  Using "Scale" ensure that the laser path will fall within the bounds of your lower reservoir.

Note: Scale is the percentage of the volume range of your sound card that the printer will use.  We highly recommend keeping it below 75% because to top 25% of sound cards ( the really loud sounds) don't come out quite right and that makes for very warped prints!


6.1.  In "Calibrate" enter the maximum print height for the reservoir you chose in the "Upper Calibration Height" field.

Note: The maximum print height is the distance between the print base level (the level at which you start a print) to the maximum height of your lower reservoir.  You calculate this by measuring the height of your wire mesh print base, and subtracting that from the height of your lower reservoir.  For example - 6 cm (height of lower reservoir) subtract 1 cm (height of print base) = 5 cm (maximum print height).

6.2.  Click inside the first set of "Actual X" and "Actual Y" values (either field will work). The laser beam should move to a new position on the calibration grid.  Measure (in mm) the X and Y coordinates of the laser beams position from the center lines on the grid and enter them in their respective fields.

6.3. Complete the upper height calibration by repeating step 6.2. for the remaining 3 sets of "Actual X" and "Actual Y" values.

7.  Remove your lower reservoir and place your calibration grid on top of your print base underneath the printer.

8.  Repeat steps 2-4 to ensure that your calibration grid is centered and aligned.

9.  Complete the lower height calibration by repeating the same process done in step 6.2. for the 4 sets of "Actual X" and "Actual Y" values.

10.  Click "Save".

11.  Replace the calibration grid with the glow paper square.  Play the signals in "Calibrated Patterns" to test out your calibrated Peachy Printer.'''


setup_audio_help = '''Some help setting up audio goes here'''
setup_drip_calibration_help = '''Purpose: This step allows the software to determine the height of the print surface in your lower reservoir so that it can send the correct layer to the printer. This process must be completed every time you physically alter the dripper or change the lower reservoir.

Process Overview:  The drip calibration process requires you to run your drip feed until the salt water fills your lower reservoir to a specific height (we recommend a minimum height of 30mm).  Meanwhile, the software counts the total number of drips it took to get to said height, then calculates the drips per mm for the lower reservoir that you chose.  This is how the software knows what level the print surface is at throughout the duration of the print.

Note: The drip rate affects the size of the drips by as much as 30%. This is an issue we plan to account for in the software by measuring the time between each drip and using that in a formula to calculate the drip size.  For now just be aware that it is still an issue.

1.  Ensure that your computer's microphone levels are at 100% and no special effects or features are enabled (monitoring, etc).

2.  Ensure that your drip system is set up correctly.  Your drip feed should be hanging from the hose hanger on the upper reservoir and running down into your lower reservoir.  You should have enough salt water in your upper reservoir to fill the lower one, and your lower reservoir should be empty.

3.  Make a mark on the outer wall of your lower reservoir.  We recommend that the mark be 30mm from the bottom of the reservoir.  A larger distance between the mark and the bottom of the reservoir will result in a more accurate and time consuming calibration.  Enter the distance between the bottom of your reservoir and the mark in the "End Height in Millimeters" field.

Note:  If the bottom of your lower reservoir isn't flat you must make an additional mark that is higher than the peak of the bottom of your reservoir, then make the measurement for the second mark from the first one.  This is because the liquid is displaced by the raised portion of the bottom of your reservoir, therefore resulting in an inaccuracy in the beginning of the calibration.  For example:  If the bottom of your reservoir has a raised bump to the height of 8mm then make a mark 10mm from the very bottom, and another mark 30mm from the mark at 10mm.

4.  Start running the drip feed at a speed of about 3 drips per second.  You should see the "Drips" number rising each time there is a drip.

Note:  If the bottom of your reservoir wasn't flat and your had to make two marks then you must click the "Reset Counter" button once the surface level of the salt water reaches your first mark.

Tip:  You may need to adjust the distance between the two aluminum rods in your drip feed so that each drip makes and breaks contact with both rods as it falls.  You can do this by sliding the upper rod and plunger up or down.

5.  Once the surface level of the salt water reaches your upper mark click the "Mark" button, then click the "Save" button.'''
cure_test_help = '''Description: In this step you'll find the ideal cure time (or laser speed). This is done by printing an "L" shaped corner at various speeds and then examining the print to determine the best cure time. If the laser moves too slowly, the resin gets exposed to too much light, resulting in a print that is overcured. Overcuring can cause a print to have very rough walls and sometimes even fail if the resin isn't able to break it's surface tension quick enough.  If the laser moves too quickly, the resin will not be exposed to enough light, resulting in a print that is undercured.  Undercuring can cause a print to have very smooth, yet soft and squishy walls, and to a strong enough effect can also cause a print to fail.  The ideal settings will result in a print that has been cured as hard as possible while still having smooth walls.  You can then fully cure the print at a later time by setting it out in sunlight, or by using a curing station. This process must be done each time that the laser is changed, or when using different resin formulas (stiff, flex, wiggle).

1.  Ensure that your drip system and printer are set up and ready to print.  This requires your upper reservoir to be placed above the printer with the drip feed hanging from it and running down to the lower reservoir which must be place directly beneath the printer.  The drip feed should have the syphon action started with the valve closed.  The lower reservoir should have about 10mm of salt water in it, and enough resin to cover the surface of the salt water.  You also must make sure that the surface level of the resin is slightly below your wire mesh print base.

2.  Ensure that your volume and microphone levels are at 100% and that all special effects and features are disabled.

3. Click the "Run Test" button.

4.  Open the valve on your drip feed.  The cure test print should begin.

5.  Once the print is complete remove it from the lower reservoir while being careful not to expose it to sunlight or other sources of UV light (this will cause it to over cure and result in an inaccurate test).

6.  Examine the print to decipher at what height from the base did the optimal cure rate occur.  The optimal cure rate is the point at which the print is cured hardest while still having smooth walls.  Measure the distance from the base of the print to this point and enter that in the "Best Height Above Base" field.  Click save.

Note:  If your cure test print did not have enough of a range to find what we described as the optimum cure rate then adjust the numbers in the "Start Speed" and "Finish Speed" fields.  Increasing the speed will result in a less cured print, decreasing the speed will result in a more cured print.'''

