import re
import string
class LuaError(Exception):
    def __init__(self, s):
        self.error_mesg = s

    def __str__(self):
        return self.error_mesg


def fun(s):
    s.replace('a', 'z')
    print(s)
    return s


if __name__ == "__main__":
    s = {1:"a", 2:"b"}
    c = "ab"

    print(fun(c), c)