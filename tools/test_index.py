import math

class Track:
    def __init__(self):
        self.history = []

t = Track()
try:
    print(t.history[-1][0])
except Exception as e:
    print("Exception:", type(e))
