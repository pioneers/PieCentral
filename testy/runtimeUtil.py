import traceback
import threading

BAD_EVENT = "BAD THINGS HAPPENED"
class BadThing:
  def __init__(self, exc_info, data):
    myThread = threading.currentThread()
    self.name = myThread.name
    self.data = data
    self.event = BAD_EVENT
    self.errorType, self.errorValue, self.traceback = exc_info

  def __str__(self):
    badThingDump = \
      ("Fatal Error in thread: %s\n"
      "Bad Event: %s\n"
      "Error Type: %s\n"
      "Error Value: %s\n"
      "Traceback: \n%s") % \
      (self.name, self.event, self.errorType, self.errorValue, "".join(traceback.format_tb(self.traceback)))
    return badThingDump