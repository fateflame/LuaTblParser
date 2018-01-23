class element:
    def __init__(self, string, flag):
        # flag 表示这是否是一个key-value对
        self.is_pair = flag
        self.string = string.strip()

    def __repr__(self):
        return self.string


class LuaParser:
    def __init__(self, orig_str):
        self.string = orig_str.strip()     # 移除头尾空格
        self.split(self.string)

    @staticmethod
    def __next_element(string, begin_pos=1):
        if begin_pos >= string.__len__()-1:        # last character
            return None
        else:
            return LuaParser.__get_an_element(string, begin_pos)

    @staticmethod
    def __get_an_element(string, begin_pos=1):
        # 从begin_pos处（含）开始，返回字符串的下一个元素以及指向下个元素尾的 后一个字符
        # 如果不存在在返回None
        if string[begin_pos] == ',':
            raise ValueError("incorrect lua table construction")
        stack_deep = 0  # 用以进行左右大括号配对
        ptr = begin_pos  # 遍历字符串的起点
        is_pair = False  # 记录是否是key-value对
        while stack_deep > 0 or (string[ptr] != ',' and string[ptr] != ';'):  # ','和';'都可以用作分隔符
            if (string[ptr] is '=' and stack_deep == 0):
                is_pair = True
            elif string[ptr] is '{':
                stack_deep += 1
            elif string[ptr] is '}':
                stack_deep -= 1
                if stack_deep < 0:
                    raise ValueError("incorrect lua table construction")
            ptr += 1
            if ptr == string.__len__()-1:       # 下一轮p将访问字符串结尾，即构造式最外层的'}'
                if stack_deep != 0:
                    raise ValueError("incorrect lua table construction")
                else:
                    break
        return element(string[begin_pos:ptr], is_pair), ptr

    @staticmethod
    def split(string):
        elements = []
        pos = 1  # skip the "{" at the beginning
        res = LuaParser.__next_element(string, pos)
        while res:  # not None
            elements.append(res[0])
            pos = res[1] + 1
            res = LuaParser.__next_element(string, pos)
        return elements


if __name__ == "__main__":
    f = open("./case.lua")
    s = f.read().strip()
    i = 1
    for e in LuaParser.split(s):
        print(i, e)
        i += 1