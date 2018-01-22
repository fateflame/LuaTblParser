import parser


class PyLuaTblParser:
    def __init__(self):
        self.lua_table = None

    def load(self, s):
    # 读取Lua table数据，输入s为一个符合Lua table定义的字符串，无返回值；若遇到Lua table格式错误的应该抛出异常；
        self.lua_table = parser.LuaTable(s)

    def dump(self):
        # 根据类中数据返回Lua table字符串
        return self.lua_table.original_str

    def loadLuaTable(self, f):
    # 从文件中读取Lua table字符串，f为文件路径，异常处理同1，文件操作失败抛出异常；
        try:
            file = open(f, 'r')
            line = file.readline()
            self.load(line)
            file.close()
        except IOError:
            raise

    def dumpLuaTable(self, f):
        # 将类中的内容以Lua table格式存入文件，f为文件路径，文件若存在则覆盖，文件操作失败抛出异常；
        file = open(f, 'w')
        file.write(self.dump())

    def loadDict(self, d):
        # 读取dict中的数据，存入类中，只处理数字和字符串两种类型的key，其他类型的key直接忽略；
        self.lua_table.table = d
        # TODO deep copy
        self.lua_table.original_str = make_string(d)
        # TODO make_string

    def dumpDict(self):
        # 返回一个dict，包含类中的数据


if __name__ == "__main__":
    test_str = '{1,"a",dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'

