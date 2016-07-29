import traceback
import multiprocessing

BAD_EVENT = "BAD THINGS HAPPENED"
class BadThing:
  def __init__(self, exc_info, data):
    self.name = multiprocessing.current_process().name
    self.data = data
    self.event = BAD_EVENT
    self.errorType, self.errorValue, tb = exc_info
    self.stackTrace = self.genStackTrace(tb)

  def genStackTrace(self, tb):
    badThingDump = \
      ("Fatal Error in thread: %s\n"
      "Bad Event: %s\n"
      "Error Type: %s\n"
      "Error Value: %s\n"
      "Traceback: \n%s") % \
      (self.name, self.event, self.errorType, self.errorValue, "".join(traceback.format_tb(tb)))
    return badThingDump

  def __str__(self):
    return self.stackTrace