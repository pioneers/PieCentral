import threading
import time
import studentCode

STUDENT_THREAD_NAME = "student_thread"

# TODO:
# 0. Set up testing code for the following features. 
# 1. Have student code throw an exception. Make sure runtime catches gracefully.
# 2. Have student code go through api to modify state. 


def runtime():
  state = [0]
  runStudentCode(state)
  while True:
    time.sleep(1)

def runStudentCode(state):
  studentThread = threading.Thread(target=runStudentCodeHelper, name=STUDENT_THREAD_NAME, args=(state,))
  studentThread.daemon = True
  studentThread.start()

def runStudentCodeHelper(state):
  nextCall = time.time()
  while True:
    studentCode.main(state)
    nextCall += 1
    time.sleep(nextCall - time.time())

runtime()