from subprocess import Popen
import sys
import time

Reset_time = 24*60*60
Time_to_reset = time.time() + Reset_time
Init = False

filename = "Main.py"
while True:

    if Init == False:
        print("\nStarting " + filename)
        p = Popen("python " + filename, shell=False)
        #p.wait()
        Init = True

    if time.time() > Time_to_reset:
        print("\nReset process")
        Time_to_reset = time.time() + Reset_time
        p.kill()
        Init = False


