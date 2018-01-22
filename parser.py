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
        # 如果类型显示为可转为key-value的键值对，则输出[key,value]
        # 转换失败时抛出异常
        if not self.is_pair:
            raise TypeError("cannot converse a non-pair object to a key-value pair")
        else:
            key_value_pattern = "\A(?P<key>(.*?))=(?P<value>(.*?))\Z"
            m = re.search(pattern=key_value_pattern, string=self.string)
            # 返回等号两侧去除首尾空格后的字符串
            rough_key = self.__remove_space(m.group("key"))
            rough_value = self.__remove_space(m.group("value"))
            value = self.__parser_value(rough_value)
            key = self.__parser_key(rough_key)
            return key, value

    @staticmethod
    def __parser_key(key_string):
        # 输入两侧空格符已被移除的字符串，返回key值
        # 字符串不能为空（作为key值），否则抛出异常（但可以是空字符串"")
        if key_string.__len__() == 0:
            raise ValueError("incorrect lua table construction")
        temp = element.__remove_brackets(key_string)
        if temp is None:            # 没有中括号包围，智能是字符串
            if not element.__remove_quotations(key_string):
                return key_string
            else:                           # 无中括号但有引号 是非法的
                raise ValueError("incorrect lua table construction")
        else:
            temp = element.__remove_space(temp)     # delete spaces between brackets and keys
            if temp.__len__() >= 2:
                temp2 = element.__remove_quotations(temp)
                # 长度大于2且两端有引号时，key是字符串（注意空字符串""不等于None）
                if temp2 is not None:
                    return temp2
            # no quotations, only int/float types are permitted
            try:
                f = float(key_string)
                return int(f) if int(f) == float(f) else float(f)
            except ValueError:
                raise ValueError("incorrect lua table construction")

    @staticmethod
    def __parser_value(value_string):
        # 输入两侧空格符已被移除的字符串，返回value值
        # 字符串不能为空（作为value值），否则抛出异常
        if value_string.__len__() == 0:
            raise ValueError("incorrect lua table construction")
        if value_string[0] == "{" and value_string [value_string.__len__()-1] == "}":
            return LuaTable(value_string)       # 递归地构造table
        else:
            if value_string.__len__() >= 2:
                temp = element.__remove_quotations(value_string)
                if temp is not None:  # string type with quotations
                    return temp
            # only int/float/nil/bool are permitted
            if value_string == "false":         # lua 中bool型用true/false表示（全小写）
                return False
            elif value_string == "true":
                return True
            elif element.__is_variable(value_string):  # not None，说明是个变量，以字母开头
                return None
            else:
                try:
                    f = float(value_string)
                    return int(f) if int(f) == float(f) else float(f)
                except ValueError:
                    raise ValueError("incorrect lua table construction")

    @staticmethod
    def __remove_space(string):
        # 去除字符串首尾的空格
        patt_str = "\A[ ]*(?P<str>(.*?))[ ]*\Z"
        return re.match(pattern=patt_str, string=string).group("str")

    @staticmethod
    def __remove_brackets(string):
        # 输入一串个字符串，检测头尾是否含有成对的中括号[]（只适用于key值外侧）
        # 如果有，则返回移除一对括号后的字符串，否则返回None
        # 如果两侧括号不匹配，抛出异常
        if string[0] == '[':
            if string[string.__len__()-1] == ']':
                # 去除头尾的括号对后返回
                return string[1:string.__len__()-1]
            else:
                raise ValueError("incorrect lua table construction")
        else:       # 没有括号则直接返回
            return None

    @staticmethod
    def __remove_quotations(string):
        # 输入一串个非空字符串，检测头尾是否含有成对的引号（只适用于str值）
        # 如果有，则返回移除一对引号后的字符串，否则返回None
        # 如果两侧引号不匹配，抛出异常
        if string.__len__() <= 1:
            raise ValueError("incorrect lua table construction")
        if string[0] == '\'' or string[0] == '\"':
            if string[string.__len__()-1] == string[0]:
                # 去除头尾的括号对后返回
                return string[1:string.__len__()-1]
            else:
                raise ValueError("incorrect lua table construction")
        else:       # 没有引号则直接返回
            return None

    @staticmethod
    def __is_variable(string):
        # 输入一个(不属于关键字的)字符串，判断该字符串是否符合variable的定义规则
        var_pattern = "\A[_a-zA-Z][\w]*\Z"
        return True if re.search(pattern=var_pattern, string=string) else False

class LuaTable:
    TblType = Enum('type', ('list', 'dict'))

    def __init__(self, string):
        self.count = 1
        self.original_str = string
        self.table = self.make_table()

    def make_table(self):
        element_list = self.split(self.original_str)
        tp = LuaTable.TblType.list  # 初始化为list
        for e in element_list:
            if e.is_pair:
                tp = LuaTable.TblType.dict  # 只有当元素中存在[key]=value式时才用dict
                break
        if tp is LuaTable.TblType.list:
            return element_list
        else:
            lua_dict = {}
            for e in element_list:
                if e.is_pair:
                    k, v = e.get_pair()
                    lua_dict[k] = v
                else:
                    v = element._element__parser_value(e.string)
                    lua_dict[self.count] = v
                    self.count += 1
            return lua_dict

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
#    print(element.is_variable("g"))


    test_str = '{1.5=5, array = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array2 = {3,6,4,},string = "value",},}'
    t1 = '{[""]=5}'
    e = LuaTable(test_str)


