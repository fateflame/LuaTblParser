class TblConstuctionError(Exception):
    def __init__(self, s="incorrect lua table construction"):
        self.error_mesg = s

    def __str__(self):
        return self.error_mesg


class PyLuaTblParser:
    def __init__(self):
        self.string = ""
        self.dict = None

    def load(self, s):
        self.string = s
        p = self.__skip(s, 0)
        self.dict = self.__get_lua_table(self.string, p)

    def loadLuaTable(self, f):
        try:
            file = open(f)
            s = file.read()
            self.load(s)
            file.close()
        except IOError as e:
            raise e

    def dumpDict(self):
        ret_dict = {}


    @staticmethod
    def __check_pos(s, begin):
        # 检查begin是否超出字符串s的最后一个字符位置
        # 每次调用可能会导致begin指针越界的行为后调用
        # （包括 +=, skip, get_comment, get_number, get_variable, get_value, get_lua_table, get_str)
        if begin >= s.__len__():
            raise TblConstuctionError

    @staticmethod
    def __get_lua_table(s, begin):
        # precondition string[begin]=='{'
        # 返回(t,end)
        # t表示得到的，从begin开始的lua表 -- 该表必然存在，否则抛出异常
        # end表示该字符串结束的后一位
        if s[begin] != '{':
            raise ValueError("cannot find '{' at the given position")
        table = {}      # 保存dict
        array = []      # 保存list
        is_list = True  # 判断是否有k-v对（需要用table保存）
        count = 1
        p = begin+1
        while True:                 # 每轮p递增的数量由具体情况决定
            p = PyLuaTblParser.__skip(s, p)        # 遇到第一个有效字符
            PyLuaTblParser.__check_pos(s, p)
            if s[p] == ',' or s[p] == ';':                  # 分隔符
                if array.__len__() == 0 and table.__len__() == 0:       # 尚未得到第一个元素
                    raise TblConstuctionError
                p = PyLuaTblParser.__skip(s, p + 1)
                PyLuaTblParser.__check_pos(s, p)
            if s[p] == '}':
                return (array, p+1) if is_list else (table, p+1)
            elif s[p] == '{':        # 递归地构造表
                ret_tbl, p = PyLuaTblParser.__get_lua_table(s, p)
                PyLuaTblParser.__check_pos(s, p)
                if is_list:
                    array.append(ret_tbl)
                else:
                    table[count] = ret_tbl
                    count += 1
            elif s[p] == '\'' or s[p] == '\"':        # (value)string，做key值时需外加方括号[]，或去除引号
                ret_s, p = PyLuaTblParser.__get_str(s, p)
                PyLuaTblParser.__check_pos(s, p)
                if is_list:
                    array.append(ret_s)
                else:
                    table[count] = ret_s
                    count += 1
            elif s[p] in "-.0123456789":        # (value)number，做key值时需外加方括号[]
                ret_num, p = PyLuaTblParser.__get_number(s, p)
                PyLuaTblParser.__check_pos(s, p)
                if is_list:
                    array.append(ret_num)
                else:
                    table[count] = ret_num
                    count += 1
            elif s[p] == '_' or s[p].isalpha():
                ret_var, p = PyLuaTblParser.__get_variable(s, p)
                PyLuaTblParser.__check_pos(s, p)
                is_normal, ret_var = PyLuaTblParser.__check_variable(ret_var)
                # key cannot be a boolean or None type, must be a value
                if not is_normal:
                    if is_list:
                        array.append(ret_var)
                    else:
                        table[count] = ret_var
                        count += 1
                else:
                    p = PyLuaTblParser.__skip(s, p)
                    PyLuaTblParser.__check_pos(s, p)
                    if s[p] == "=":     # is a k-v pair
                        p = PyLuaTblParser.__skip(s, p + 1)     # +1 to skip =
                        PyLuaTblParser.__check_pos(s, p)
                        value, p = PyLuaTblParser.__get_value(s, p)
                        PyLuaTblParser.__check_pos(s, p)
                        if is_list:
                            is_list = False
                            count = PyLuaTblParser.__list_to_dict(array, table) + 1
                        table[ret_var] = value
                    # else: it's a normal variable, treated as null value, ignore
            elif s[p] == '[':       # must be a k-v pair
                p += 1
                PyLuaTblParser.__check_pos(s, p)
                key = None      # 用于接收返回的key
                if s[p] in "-.0123456789":        # (key)number,
                    key, p = PyLuaTblParser.__get_number(s, p)
                elif s[p] == '\'' or s[p] =='\"':
                    key, p = PyLuaTblParser.__get_str(s, p)
                else:
                    raise TblConstuctionError
                p = PyLuaTblParser.__skip(s, p)       # skip spaces
                PyLuaTblParser.__check_pos(s, p)
                if s[p] != ']':
                    raise TblConstuctionError
                p = PyLuaTblParser.__skip(s, p + 1)      # "+1" to skip ']'
                PyLuaTblParser.__check_pos(s, p)
                if s[p] != '=':
                    raise TblConstuctionError
                p = PyLuaTblParser.__skip(s, p + 1)      # "+1" to skip '='
                PyLuaTblParser.__check_pos(s, p)
                value, p = PyLuaTblParser.__get_value(s, p)
                if is_list:
                    is_list = False
                    count = PyLuaTblParser.__list_to_dict(array, table) + 1
                table[key] = value
            else:
                raise TblConstuctionError

    @staticmethod
    def __list_to_dict(li, di):   # pass test
        # li, di分别为一个列表和一个 空的字典
        # 将li中元素按序复制到字典中（对象则复制其引用）
        # 返回元素的个数
        i = 1
        for e in li:
            di[i] = e
            i += 1
        return i

    @staticmethod
    def __get_value(s, begin):
        # precondition: s[begin] is a valid character(skip the spacecharacters and comments)
        # return (e, p).
        # e is a legal value type(nil，bool，number，str，table)
        if s[begin] == '{':
            return PyLuaTblParser.__get_lua_table(s, begin)
        elif s[begin] == "'" or s[begin] == '"':
            return PyLuaTblParser.__get_str(s, begin)
        elif s[begin] in "-.0123456789":
            return PyLuaTblParser.__get_number(s, begin)
        elif s[begin] == '_' or s[begin].isalpha():
            var, p = PyLuaTblParser.__get_variable(s, begin)
            is_normal, ret_var = PyLuaTblParser.__check_variable(var)
            return (None, p)if is_normal else (ret_var, p)      # 未定义的变量将被视为None

    @staticmethod
    def __check_variable(var):
        # check if it's a boolean or NULL
        # return (is_normal, ret_var)。
        # is_normal为bool变量，为假表示var是一个bool变量或None变量。为真表示var是个普通字符串变量
        if var == 'nil':
            return False, None
        elif var == "true":
            return False, True
        elif var == "false":
            return False, False
        else:
            return True, var

    @staticmethod
    def __get_variable(s, begin):
        # precondition:s[begin] in string.letters
        # return (var, p),var表示解析得到的字符串，p表示数字最后一个字符的后一个字符所在位置
        if not s[begin].isalpha() and s[begin] != '_':
            raise ValueError("cannot find letters or '_' at the given position")
        p = begin+1
        while p < s.__len__():
            if not s[p].isalnum() and s[p] != '_':
                break
            p += 1
        return s[begin: p], p

    @staticmethod
    def __get_number(s, begin):       # pass test
        # precondition:s[begin] in '0123456789.-'
        # return (num, p),num表示解析得到的数字，p表示数字最后一个字符的后一个字符所在位置
        if s[begin] not in '-0.123456789':
            raise ValueError("cannot find digit character at the given position")
        p = begin+1
        while p < s.__len__() and s[p] in '-+0.123456789eE':
            p += 1
            if begin >= s.__len__():
                break
        num_str = s[begin: p]
        try:
            f = float(num_str)
            if "e" in num_str or "E" in num_str:
                return f, p
            i = int(f)      # 不会抛出异常
            num = i if f == i else f
            return num, p
        except ValueError as e:
            raise TblConstuctionError(e.__str__())

    @staticmethod
    def __get_comment(s, begin):
        # precondition: string[begin:begin+2] == '--'
        # 返回注释结束的后一个字符所在的序号（不需要提取comment里面的内容）
        if s[begin:begin+2] != '--':
            raise ValueError("cannot find start '-' at the given position")
        if s[begin: begin + 4] == '--[[':  # 多行注释
            begin += 4  # skip '--[['
            if begin >= s.__len__() - 1:  # 字符串结束前没有足够空间，存到注释结束符
                raise TblConstuctionError("incorrect lua table construction")
            while s[begin: begin + 2] != ']]':  # 以']]'结束，注释内部不需要担心引号
                begin += 1
                if begin >= s.__len__()-1:  # 字符串结束前没有足够空间，存到注释结束符
                    raise TblConstuctionError("incorrect lua table construction")
            begin += 2  # skip ']]'
        else:  # 单行注释
            begin += 2  # skip '--'
            while begin < s.__len__():      # 未访问完字符串
                if s[begin] == '\n':
                    return begin+1
                begin += 1
        return begin

    @staticmethod
    def __skip(s, begin):        # pass test
        # 从给定位置开始，跳过遇到的空格和注释
        # 返回跳过后的第一个有效字符的位置begin
        # 如果string[begin]就是非空格或注释，返回begin
        # 重要：如果后续没有其他有效字符了，则返回字符串结尾的后一个字符位置
        while True:
            if begin >= s.__len__():
                return begin
            if s[begin].isspace():
                begin += 1
            elif s[begin: begin+2] == '--':
                begin = PyLuaTblParser.__get_comment(s, begin)
            else:
                break
        return begin

    @staticmethod
    def __get_str(s, begin):     # pass test
        # precondition string[begin]='\'' or '"'，即字符开始的位置
        # 返回(s,p)。s表示引号内的字符串，p指向字符串后引号的下一个位置
        p = PyLuaTblParser.__get_quotation(s, begin)
        ret_s = PyLuaTblParser.__parse_str(s[begin+1:p-1])      # 跳过首尾的引号
        return ret_s, p

    @staticmethod
    def __get_quotation(s, begin):     #pass test
        # precondition: string[begin]=='\''or '\"'
        # 返回字符串右引号位置的下一个序号
        if s[begin] != '\'' and s[begin] != '\"':
            raise ValueError("cannot find start quotation at the given position")
        p = begin + 1
        PyLuaTblParser.__check_pos(s, p)
        while not (s[begin] == s[p]):       # 遇到匹配的右引号跳出
            if p == s.__len__()-1:     # 最后一个字符，没有找到对应的后引号
                raise TblConstuctionError("incorrect lua table construction")
            if s[p] == '\\':
                p += 2      # 跳过下一个字符（与斜杠共同构成转义字符）
                continue
            p += 1
        return p+1

    @staticmethod
    def __parse_str(s):        # pass test
        # 传入一串字符串（不带首尾引号），将其中转义字符替换为应有的意思
        s = s.replace('\\\\','\\')
        s = s.replace("\\'", "'")
        s = s.replace('\\"', '"')
        s = s.replace("\\b", "\b")
        s = s.replace("\\000", "\000")
        s = s.replace("\\n", "\n")
        s = s.replace("\\v", "\v")
        s = s.replace("\\t", "\t")
        s = s.replace("\\r", "\r")
        s = s.replace("\\f", "\f")
        return s


if __name__ == "__main__":
    f = open('./requirements')
    s = '{array1 = {65,23,5,},dict = {mixed = {43,54.33,false,9,string = "value",},array = {3,6,4,},string = "value",},}'
    s = f.read()
    c = PyLuaTblParser.__get_lua_table(s, 0)
    print(c[0], c[1])
