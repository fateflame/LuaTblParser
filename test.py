import re
import string
class LuaError(Exception):
    def __init__(self, s):
        self.error_mesg = s

    def __str__(self):
        return self.error_mesg

if __name__ == "__main__":
    s= '{"array with 1 element",}'
    print(s[1].isspace())