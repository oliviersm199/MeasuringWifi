# MeasuringWifi

To install first run the bash script:

  - sudo ./installation

Then call measurement.py as follows from the terminal:
  - python measurement.py

It will prompt you to enter your location, use a location scheme like 1E to represent first floor Mclennan East. 

The date and time will automatically get written and you will have two files as output:
  - Access Point: Information about all the access points
  - Connection Info: Information about your particular connection

We can hand this off to the individuals in our team doing analysis and they should be able to answer several questions
from the project. The only question we still have left is how many users are on the particular network at a time.

I was thinking of obtaining this information using NMap. A new version will have this additional feature, I will continue trying to
work on this tomorrow. 

# FAQ

First step of getting all wireless connection info may not function properly. There is a bug in the airport command, 
when it is called frequently it sometimes fails.
