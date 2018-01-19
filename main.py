import re


class PyLuaTblParser:
    def __init__(self, string):
        # 将lua table构造式保存在类内
        self.table_str = string
        str = string[1:string.__len__()-1]          # 去除首尾大括号
        self.lua_table = {}
        self.count = 0

    @staticmethod
    def __remove_space(str):
        return str.replace(" ", "")  # remove space

    @staticmethod
    def __next_element(str):
        # 输入一个字符串，寻找其中第一次出现单词的位置。如"1", 2, bb, "a_b"
        # 这个对象可能是key，也可能是value
        # 返回一个三元组(start,end,str)表示找到串的位置和内容，如果没有则返回None
        pattern_sig = "(?P<quotation>\")?[\w_.]+(?(quotation)\")"   # 两侧判断是否有引号“”，[\w_.]匹配元素，由逗号分隔
        m_word = re.search(pattern=pattern_sig, string=str)
        m_braces = PyLuaTblParser.__next_pair_braces(str)
        if m_word:
            if m_braces:
                if m_word.start() < m_braces[0]:
                    return {m_word.start(), m_word.end(),m_word.group(0)}
                else:
                    return m_braces
            else:
                return {m_word.start(), m_word.end(), m_word.group(0)}
        else:           # m_word == None
            return m_braces if m_braces else None

    @staticmethod
    def __next_pair_braces(str):
        # 找出字符串中第一次出现的，互相呼应的大括号所在位置
        # 返回一个三元组{begin, end, str}表示该字符串开始的位置，结束的位置+1，字符串内容
        # 如果不存在返回None
        start = 1
        end = 2
        str = ""
        return {start, end, str}

    def __next_pair(self, str):
        # 输入一个无空格的字符串，从头开始找到table中第一对元素
        m = PyLuaTblParser.__next_element(str)
        if m is None:       # 处理完毕
            return None
        pos_end = m[1]
        if pos_end != '=':                                # 无key值的独立value
            value = m[2]
            self.count += 1
            self.lua_table[self.count] = PyLuaTblParser(value) if value[0] is '{' else value
            return str[pos_end+1, str.__len__()]          # 截去已处理部分，+1截去分隔符“，”



# array1 = {65,23,5,},
#
if __name__ == "__main__":
    test_str = '{1,"a",dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
    test_str = test_str.replace(" ", '')
    patt_equ1 = "(?P<quotation>\")?[\w_.]+(?(quotation)\")"
    m1 = re.search(pattern=patt_equ1, string=test_str)
    pattern_sig = "[\w_\"]+,"
    pat = "(?P<key>[\w_\"]+)=(?P<value>{[\w_\",.={}]+})"
    m2 = re.search(pattern=patt_equ1, string=test_str)
   # print(m2.groupdict())
    tuple = (1,2,"aa")
    print(tuple[0], tuple[2])
