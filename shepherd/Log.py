import datetime
import Shepherd
from Utils import *

last_header = None
#pylint: disable=redefined-builtin, no-member
def log(Exception):
    global last_header
    # if Shepherd.match_number <= 0:
    #     return
    now = datetime.datetime.now()
    filename = str(now.month) + "-" + str(now.day) + "-" + str(now.year) +\
               "-match-"+ str(Shepherd.match_number) +".txt"
    print("a normally fatal exception occured, but Shepherd will continue to run")
    print("all known details are logged to logs/"+filename)
    file = open("logs/"+filename, "a+")
    file.write("\n========================================\n")
    file.write("a normally fatal exception occured.\n")
    file.write("all relevant data may be found below.\n")
    file.write("match: " + str(Shepherd.match_number)+"\n")
    file.write("game state: " + str(Shepherd.game_state)+"\n")
    file.write("gold alliance: " + str(Shepherd.alliances[ALLIANCE_COLOR.GOLD])+"\n")
    file.write("blue alliance: " + str(Shepherd.alliances[ALLIANCE_COLOR.BLUE])+"\n")
    file.write("game timer running?: " + str(Shepherd.game_timer.is_running())+"\n")
    file.write("the last received header was:" + str(last_header)+"\n")
    file.write("a stacktrace of the error may be found below\n")
    file.write(str(Exception))
    file.close()
