# debug, info, warn, error, result
priorities = ['d', 'i', 'w', 'e', 'r']
mode = 0
    
def log(msg: str, priority: str):
    if mode <= priorities.index(priority):
        print("[" + priority + "] " + msg)

def d(msg: str):
    if mode == 0:
        print("[d] " + msg)

def i(msg: str):
    if mode <= 1:
        print("[i] " + msg)

def w(msg: str):
    if mode <= 2:
        print("[w] " + msg)

def e(msg):
    if mode <= 3:
        print(msg)

def r(msg):
    if mode <= 4:
        print(msg)