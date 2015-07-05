#!/usr/bin/env python
#
#  raspiLapseCam.py
#
#  Created by James Moore on 28/07/2013.
#  Modified by James Moore on 13/11/2013.
#  Copyright (c) 2013 Fotosyn. All rights reserved.
#
#  Raspberry Pi is a trademark of the Raspberry Pi Foundation.

#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:

#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.>

#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#  The views and conclusions contained in the software and documentation are those
#  of the authors and should not be interpreted as representing official policies,
#  either expressed or implied, of the FreeBSD Project.

# This script sets up and runs a Python Script which, at intervals invokes a capture 
# command to the Raspberry Pi camera, and stores those files locally in a dynamically
# named folder.

# To invoke, copy this script to an easy to find file location on your Raspberry Pi
# (eg. /home/pi/), log into your Raspberry Pi via terminal and type:
#
# sudo python /your/file/location/raspiLapseCam.py (add &) if you wish to run as a
# background task. A process ID will be shown which can be ended with

# sudo kill XXXX (XXXX = process number)

# Based on your settings the application will now begin capturing images
# saving them to your chosen file location (same as current location of this file as default.

# Import some frameworks
import os
import signal
import sys
import time
import RPi.GPIO as GPIO
import logging
from datetime import datetime
import boto
from boto.s3.key import Key
from multiprocessing import Process

# Grab the current datetime which will be used to generate dynamic folder names
d = datetime.now()
initYear = "%04d" % (d.year) 
initMonth = "%02d" % (d.month) 
initDate = "%02d" % (d.day)
initHour = "%02d" % (d.hour)
initMins = "%02d" % (d.minute)

s3 = boto.connect_s3()

# Define the location where you wish to save files. Set to HOME as default. 
# If you run a local web server on Apache you could set this to /var/www/ to make them 
# accessible via web browser.
bucketName = "timelapse_AKIAIZNHJLCNCC6U2EZA".lower()
folderToSave = "timelapse_" + str(initYear) + str(initMonth) + str(initDate) + str(initHour) + str(initMins)
locationToSave = "/home/pi/py/timelapse/" + folderToSave
os.mkdir(locationToSave)

# Set up a log file to store activities for any checks.
logging.basicConfig(filename="/var/log/timelapse.log",level=logging.DEBUG)
logging.debug(" R A S P I L A P S E C A M -- Started Log for " + str(locationToSave))
logging.debug(" Support at http://fotosyn.com/timelapse/")

logging.debug("Creating new bucket with name: " + bucketName)
bucket = s3.create_bucket(bucketName)

# Set the initial serial for saved images to 1
fileSerial = 0

outPin = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(outPin, GPIO.OUT)

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    GPIO.cleanup()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def handleLight(enabled):
    if (enabled):
        GPIO.output(outPin,True)
    else:
        GPIO.output(outPin,False)

def turnLightOn():
    handleLight(True)

def turnLightOff():
    handleLight(False)

def writeToS3(key, fileName):
    #write to S3    
    k = Key(bucket)
    k.key = key

    logging.debug("Uploading some data to " + bucketName + " with key: " + k.key)
    k.set_contents_from_filename(fileName)  

    logging.debug("Deleting file " + fileName)
    os.remove(fileName)

if __name__ == '__main__':    
    # Run a WHILE Loop of infinitely
    while True:
        
        d = datetime.now()
        if d.hour < 99:
            turnLightOn();
            # Set FileSerialNumber to 000X using four digits
            fileSerialNumber = "%04d" % (fileSerial)
            
            # Capture the CURRENT time (not start time as set above) to insert into each capture image filename
            hour = "%02d" % (d.hour)
            mins = "%02d" % (d.minute)
            
            # Define the size of the image you wish to capture. 
            imgWidth = 1600 # Max = 2592 
            imgHeight = 1200 # Max = 1944
            logging.debug(" ====================================== Saving file at " + hour + ":" + mins)
        
            # Capture the image using raspistill. Set to capture with added sharpening, auto white balance and average metering mode
            # Change these settings where you see fit and to suit the conditions you are using the camera in
            imageName = "img_" + str(fileSerialNumber) + ".jpg"
            fileName = str(locationToSave) + "/" + imageName
            os.system("raspistill --nopreview -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + str(fileName) +  " -q 50 -sh 65 --ISO 100 -ss 40000 -awb off -awbg 1.3,1.5 -mm average -v")
            turnLightOff();

            # Write out to log file
            logging.debug(' Image saved: ' + str(fileName))

            ts = time.time()
            writeToS3(folderToSave + "/" + imageName,fileName,)            
            tt = time.time() - ts

            # Increment the fileSerial
            fileSerial += 1
            
            # Wait 5 seconds before next capture
            logging.debug("Sleeping for " + str(600-tt) + " seconds")
            time.sleep(600 - tt)
            
        else:
            
            # Just trapping out the WHILE Statement
            print " ====================================== Doing nothing at this time"

