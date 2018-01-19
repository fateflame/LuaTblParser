from enum import Enum
import re


class element:
    def __init__(self, string, flag):
        # flag 表示这是否是一个key-value对
        self.is_pair = flag
        self.string = string

    def __repr__(self):
        return self.string

    def get_pair(self):
        if not self.is_pair:
            raise TypeError("cannot converse a non-pair object to a key-value pair")
        else:
            key_pattern = "\A[ ]*(?P<total>(?P<brace>\[[\'\"])?(?P<key>[\w_. ]+)(?(brace)[\'\"]\]))[ ]*="
            val_pattern = '=[ ]*(?P<val>(.*?))[ ]*\Z'
            m = re.match(pattern=key_pattern, string=self.string)
            value = re.search(pattern=val_pattern, string=self.string)
            if not m or not value:           # m==None||value==None
                raise ValueError("incorrect lua table construction")
            else:
                keyword = m.group("key")
                value = value.group("val")
                if m.group("total") == m.group("key"):         # 不带有方括号：'["..."]'，有方括号时，空格当做字符处理
                    # 判断key中间是否有空格
                    keyword = self.__romove_space(keyword)      # 删除首尾空格
                    if re.search(pattern=" ", string=keyword):      # 形如{a b}为非法构造式，分隔符必须为,或；
                        raise ValueError("incorrect lua table construction")
                return keyword, value

    @staticmethod
    def __romove_space(string):
        # 去除字符串首尾的空格
        patt_str = "\A[ ]*(?P<str>(.*?))[ ]*\Z"
        return re.match(pattern=patt_str, string=string).group("str")


class LuaTable:
    TblType = Enum('type', ('list', 'dict'))

    def __init__(self, string):
        self.count = 1
        self.original_str = string

    def make_table(self):
        element_list = self.split(self.original_str)
        tp = LuaTable.TblType.list  # 初始化为list
        for e in element:
            if e.is_pair:
                tp = LuaTable.TblType.dict  # 只有当元素中存在[key]=value式时才用dict
                break
        if tp is LuaTable.TblType.list:
            return element_list



    @staticmethod
    def split(string):
        elements = []
        pos = 1         # skip the "{" at the beginning
        res = LuaTable.__next_element(string, pos)
        while res:          # not None
            elements.append(res[0])
            pos = res[1]+1
            res = LuaTable.__next_element(string, pos)
        return elements

    @staticmethod
    def __next_element(string, begin_pos=1):
        if begin_pos >= string.__len__()-1:        # no elements contained
            return None
        else:
            return LuaTable.__get_an_element(string, begin_pos)

    @staticmethod
    def __get_an_element(string, begin_pos=1):
        # 从begin_pos处（含）开始，返回字符串的下一个元素以及指向下个元素尾的 后一个字符，如果不存在在返回None
        if string[begin_pos] == ',':
            raise ValueError("incorrect lua table construction")
        stack_deep = 0      # 用以进行左右大括号配对
        ptr = begin_pos       # 遍历字符串的起点
        is_pair = False     # 记录是否是key-value对
        while stack_deep > 0 or (string[ptr] != ','and string[ptr] != ';'):     # ','和';'都可以用作分隔符
            if string[ptr] is '=' and stack_deep == 0:
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


if __name__ == "__main__":
    patt_key = "[ ]*(?P<total>(?P<brace>\[[\'\"])?(?P<main>[\w_. ]+)(?(brace)[\'\"]\]))[ ]*="
    string ='arrayff = {65,23,5,}'
    m =re.match(patt_key, string)
    keyword = m.group("main")
    val_pattern = '=[ ]*(?P<val>(.*?))[ ]*\Z'
    print(element('["a "] =1 ', True).get_pair())

    test_str = '{array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
    e = LuaTable.split(test_str)
    for ele in e:
        print(ele, ele.is_pair)

