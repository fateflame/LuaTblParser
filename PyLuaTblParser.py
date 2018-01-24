

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
        while begin < string.__len__()-1:
            if string[begin] == ' ':
                begin += 1
                continue
            elif string[begin] == '-':
                begin = PyLuaTblParser.__get_comment(string, begin)
                continue
            elif string[begin] == '{':        # dict直接作为value
                ptr = PyLuaTblParser.__get_brace(string, begin)
                return PyLuaTblParser().load(string[begin:ptr+1]), ptr+1
            elif string[begin] == '\'' or string[begin] =='\"':       # str直接作为value
                p = PyLuaTblParser.__get_quotation(string, begin)
                temp = PyLuaTblParser.__parse_str(string[begin+1, p-1])     # 将转义字符转换为对应字符
                return temp, p        # 跳过字符串首尾引号
            else:
                ptr = begin
                while string[ptr] != ',' and string[ptr] != ';':
                    if ptr == string.__len__()-1:
                        break
                    if string[ptr] == "'" or string[ptr] == '"':
                        ptr = PyLuaTblParser.__get_quotation(string, ptr)
                        continue
                    elif string[ptr] == '{':
                        ptr = PyLuaTblParser.__get_brace(string, ptr)
                        continue
                    elif string[ptr] == '-':
                        ptr = PyLuaTblParser.__get_comment(string,ptr)
                    ptr += 1
                # TODO 处理得到的一串数据并返回
                return string[begin: ptr]

    @staticmethod
    def __get_brace(string, begin):
        # precondition: string[begin] == '{'
        # 返回括号部分结束的后一个字符所在位置
        if string[begin] != '{':
            raise ValueError("cannot find '{' at the given position")
        stack_deep = 1  # 用以进行左右大括号配对
        ptr = begin + 1  # skip '{'
        while stack_deep > 0:  # 考虑到大括号可以嵌套
            if string[ptr] == '\'' or string[ptr] == '\"':  # 嵌套字符串
                ptr = PyLuaTblParser.__get_quotation(string, ptr)
                continue
            elif string[ptr] == '-':
                ptr = PyLuaTblParser.__get_comment(string, ptr)
                continue
            if string[ptr] == '{':
                stack_deep += 1
            elif string[ptr] == '}':
                stack_deep -= 1
                if stack_deep < 0:
                    raise ValueError("incorrect lua table construction")
            ptr += 1
        return ptr

    @staticmethod
    def __get_comment(string, begin):
        # precondition: string[begin] == '-'
        # 返回注释结束的后一个字符所在的序号
        if string[begin] != '-':
            raise ValueError("cannot find start '-' at the given position")
        if string[begin: begin + 2] == '--':  # 注释
            if string[begin: begin + 4] == '--[[':  # 多行注释
                begin += 4  # skip '--[['
                while string[begin: begin + 2] != ']]':  # 以']]'结束，注释内部不需要担心引号
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
            return begin
        else:  # '-'单独出现作为减号
            return begin+1

    @staticmethod
    def __get_quotation(string, begin):     #pass test
        # precondition: string[begin]=='\''or '\"'
        # 返回字符串右引号位置的下一个序号
        if string[begin] != '\'' and string[begin] != '\"':
            raise ValueError("cannot find start quotation at the given position")
        p = begin + 1
        while not (string[begin] == string[p]):       # 遇到匹配的右引号跳出
            if p == string.__len__()-1:     # 没有找到对应的后引号
                raise ValueError("incorrect lua table construction")
            if string[p] == '\\':
                p += 2      # 跳过下一个字符（与斜杠共同构成转义字符）
                continue
            p += 1
        return p+1

    @staticmethod
    def __parse_str(string):        # pass test
        # 传入一串字符串（不带首尾引号），将其中转义字符替换为应有的意思
        string = string.replace('\\\\','\\')
        string = string.replace("\\'", "'")
        string = string.replace('\\"', '"')
        string = string.replace("\\b", "\b")
        string = string.replace("\\000", "\000")
        string = string.replace("\\n", "\n")
        string = string.replace("\\v", "\v")
        string = string.replace("\\t", "\t")
        string = string.replace("\\r", "\r")
        string = string.replace("\\f", "\f")
        return string

    @staticmethod
    def __skip_seperator(string, begin):
        # 从begin（含）位置开始，跳过分隔符（，/；）直至下一个字符串开始处
        # 返回指向下一个字符串开始处的序号p，或字符串末尾
        a = 1

if __name__ == "__main__":
    f = open('./case.lua')
    s = f.read().strip()
    f.close()
    temp = PyLuaTblParser._PyLuaTblParser__next_element(s, 1)
