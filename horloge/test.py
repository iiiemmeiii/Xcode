import time as t
import datetime as dt


a = "1234"
b = "1234"
c = hex(id(b))
print(hex(id(a)), hex(id(b)), c, flush=True)
