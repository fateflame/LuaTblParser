class Element:
    def __init__(self):
        self.is_pair = False
        self.single = ""
        self.pair = ("", "")


class PyLuaTblParser:
    def __init__(self):
        self.string = ""

    def load(self, s):
        self.string = s.strip()      # remove the space characters
        str_length = self.string.__len__()
        if self.string[0] != '{' or self.string[str_length-1] != '}':
            raise ValueError("incorrect lua table construction")

        p = 1           # skip the first '{'
        while p < str_length-1:
            e = self.__next_element(self.string, p)


    @staticmethod
    def __next_element(string, begin):
        # 返回(e,end)
        # e表示从begin（含）开始的，下一个合法字符串解析出的对象（Element形式，key-value/single value)
        # end表示该字符串结束的后一位
        # 若不存在则返回None
        in_quotation = False        # 用以判断当前是否在引号内（字符串的部分）
        stack_deep = 0  # 用以进行左右大括号配对
        while begin < string.__len__()-1:
            if string[begin] == '-':
                if string[begin, begin + 2] == '--':  # 注释
                    if string[begin, begin + 4] == '--[[':  # 多行注释
                        begin += 4  # skip '--[['
                        while string[begin: begin + 2] != ']]':  # 以']]'结束
                            if begin >= string.__len__() - 1:  # 注释结束前没有遇到结束符
                                raise ValueError("incorrect lua table construction")
                            begin += 1
                        begin += 2  # skip ']]'
                    else:  # 单行注释
                        begin += 2  # skip '--'
                        while string[begin] != '\t':  # 以换行符结束
                            if begin >= string.__len__() - 1:  # 注释结束前没有遇到结束符
                                raise ValueError("incorrect lua table construction")
                            begin += 1
                        begin += 1  # skip '\t'
                else:  # '-'不能单独出现
                    raise ValueError("incorrect lua table construction")
            if string[begin] == '\'':


    @staticmethod
    def __skip_seperator(string, begin):
        # 从begin（含）位置开始，跳过分隔符（，/；）直至下一个字符串开始处
        # 返回指向下一个字符串开始处的序号p，或字符串末尾