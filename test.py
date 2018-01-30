class test(Exception):
    def __init__(self, s):
        self.d = {1:s}

    def __getitem__(self, item):
        return self.d[item]

    def __setitem__(self, key, value):
        print "set", key, value
        self.d[key]=value


if __name__ == "__main__":
    d = test("aaa")
    d[2] = "bbb"
    print d[1]



