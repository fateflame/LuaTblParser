class TblConstuctionError(Exception):
    def __init__(self, s="incorrect lua table construction"):
        self.error_mesg = s

    def __str__(self):
        return self.error_mesg


class PyLuaTblParser:
    def __init__(self):
        self.string = ""

    def load(self, s):
        self.string = s
        p = self.skip(s, 0)
        ret = self.__get_lua_table(self.string, p)

    @staticmethod
    def __get_lua_table(s, begin):
        # precondition string[begin]=='{'
        # 返回(t,end)
        # t表示得到的，从begin开始的lua表--必然存在，否则抛出异常
        # end表示该字符串结束的后一位
        if s[begin] != '{':
            raise ValueError("cannot find '{' at the given position")
        table = {}      # 保存dict
        array = []      # 保存list
        is_list = True  # 判断是否有k-v对（需要用table保存）
        count = 1
        p = begin+1

        while True:
            p = PyLuaTblParser.skip(s, p)        # 遇到第一个有效字符
            if p >= s.__len__():
                raise TblConstuctionError
            if s[p] == ',' or s[p] == ';':                  # 分隔符
                if array.__len__() == 0 and table.__len__() == 0:       # 尚未得到第一个元素
                    raise TblConstuctionError
                p += 1
            if s[p] == '}':
                return array if is_list else table
            elif s[p] == '{':        # 递归地构造表
                ret_tbl, p = PyLuaTblParser.__get_lua_table(s, p)
                if is_list:
                    array.append(ret_tbl)
                else:
                    table[count] = ret_tbl
                    count += 1
            elif s[p] == '\'' or s[p] == '\"':        # (value)string，做key值时需外加方括号[]，或去除引号
                ret_s, p = PyLuaTblParser.get_str(s, p)
                if is_list:
                    array.append(ret_s)
                else:
                    table[count] = ret_s
                    count += 1
            elif s[p] in "-.0123456789":        # (value)number，做key值时需外加方括号[]
                # TODO finish get_number()
                ret_num,p = PyLuaTblParser.get_number(s, p)
                if is_list:
                    array.append(ret_num)
                else:
                    table[count] = ret_num
                    count += 1
            elif s[p] == '_' or s[p].isalpha():
                # TODO finish get_variable()
                ret_var, p = PyLuaTblParser.get_variable(s, p)
                # TODO finish check_variable() to check if it's a boolean or NULL
                is_normal, ret_var = PyLuaTblParser.check_variable(ret_var)
                # key cannot be a boolean or None type
                if not is_normal:
                    if is_list:
                        array.append(ret_var)
                    else:
                        table[count] = ret_var
                        count += 1
                else:
                    p = PyLuaTblParser.skip(s, p)
                    if s[p] == "=":     # is a k-v pair
                        p = PyLuaTblParser.skip(s, p)
                        # TODO get_value(s,p) return a legal value type(nil，bool，number，str，table)
                        value = PyLuaTblParser.get_value(s, p)
                        if is_list:
                            is_list = False
                            # TODO add function to trans list to dict
                            list_to_dict(array, table)
                        table[ret_var] = value
                    # else: it's a normal variable, treated as null value, ignore
            elif s[p] == '[':       # must be a k-v pair
                p += 1
                if s[p] in "-.0123456789":        # (key)number,
                    key, p = PyLuaTblParser.get_number(s, p)
                elif s[p] == '_' or s[p].isalpha():
                    key, p = PyLuaTblParser.get_variable(s, p)
                p = PyLuaTblParser.skip(s, p)
                if s[p] != ']':
                    raise TblConstuctionError
                p = PyLuaTblParser.skip(s, p+1)      # "+1" to skip ']'
                if s[p] != '=':
                    raise TblConstuctionError
                p = PyLuaTblParser.skip(s, p+1)
                value, p = PyLuaTblParser.get_value(s, p)
                if is_list:
                    is_list = False
                    # TODO add function to trans list to dict
                    list_to_dict(array, table)
                table[key] = value


    @staticmethod
    def __get_comment(s, begin):
        # precondition: string[begin:begin+2] == '--'
        # 返回注释结束的后一个字符所在的序号
        if s[begin:begin+2] != '--':
            raise ValueError("cannot find start '-' at the given position")
        if s[begin: begin + 4] == '--[[':  # 多行注释
            begin += 4  # skip '--[['
            while s[begin: begin + 2] != ']]':  # 以']]'结束，注释内部不需要担心引号
                if begin >= s.__len__() - 1:  # 注释结束前没有遇到结束符
                    raise TblConstuctionError("incorrect lua table construction")
                begin += 1
            begin += 2  # skip ']]'
        else:  # 单行注释
            begin += 2  # skip '--'
            while s[begin] != '\n':  # 以换行符结束
                if begin >= s.__len__() - 1:  # 注释结束前没有遇到结束符
                    raise TblConstuctionError("incorrect lua table construction")
                begin += 1
            begin += 1  # skip '\t'
        return begin

    @staticmethod
    def skip(s, begin):        # pass test
        # 从给定位置开始，跳过遇到的空格和注释
        # 返回跳过后的第一个有效字符的位置begin
        # 如果string[begin]就是非空格或注释，返回begin
        while True:
            if begin >= s.__len__():
                raise TblConstuctionError
            if s[begin].isspace:
                begin += 1
                continue
            if s[begin: begin+2] == '--':
                begin = PyLuaTblParser.__get_comment(s, begin)
            else:
                break
        return begin

    @staticmethod
    def get_str(s, begin):     # pass test
        # precondition string[begin]='\'' or '"'，即字符开始的位置
        # 返回(s,p)。s表示引号内的字符串，p指向字符串后引号的下一个位置
        p = PyLuaTblParser.__get_quotation(s, begin)
        ret_s = PyLuaTblParser.__parse_str(s[begin:p])
        return ret_s, p

    @staticmethod
    def __get_quotation(s, begin):     #pass test
        # precondition: string[begin]=='\''or '\"'
        # 返回字符串右引号位置的下一个序号
        if s[begin] != '\'' and s[begin] != '\"':
            raise ValueError("cannot find start quotation at the given position")
        p = begin + 1
        while not (s[begin] == s[p]):       # 遇到匹配的右引号跳出
            if p == s.__len__()-1:     # 没有找到对应的后引号
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
    f = open('./case.lua')
    s1 = f.readline()
    ss = "ll\n kjf"
    f.close()
    temp = PyLuaTblParser.get_str(s1, 0)
    print(temp[0], s1[temp[1]])
