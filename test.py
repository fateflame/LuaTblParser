class LuaError(Exception):
    def __init__(self, s):
        self.error_mesg = s

    def __str__(self):
        return self.error_mesg


def fun1(s):
    print (s,1)

def fun2(s):
    print (s, 2)

def to_string(obj):
    func_dict = {
        dict: fun1,
        list: fun2
    }
    func_dict[type(obj)](obj)


if __name__ == "__main__":
    s =None
    print (s == None)

