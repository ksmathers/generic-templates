
g_symbolcount = 0
def gensym(prefix="sym"):
    """Generate a unique symbol"""
    global g_symbolcount
    g_symbolcount += 1
    return f"{prefix}{g_symbolcount}"

class Instruction:
    def __init__(self, opcode, arg1=None, arg2=None):
        self.op = [opcode, arg1, arg2]

    @classmethod
    def LABEL(cls, label): # NOSONAR
        return Instruction('LABEL', label)
    @classmethod
    def PUSH(cls, reg): # NOSONAR
        return Instruction('PUSH', reg)
    @classmethod
    def POP(cls, reg): # NOSONAR
        return Instruction('POP', reg)
    @classmethod
    def ADD(cls, reg, const): # NOSONAR
        return Instruction('ADD', reg, const)
    @classmethod
    def JMP(cls, label): # NOSONAR
        return Instruction('JMP', label)
    @classmethod
    def JMPIF(cls, label): # NOSONAR
        return Instruction('JMPIF', label)
    @classmethod
    def EMIT(cls, text): # NOSONAR
        return Instruction('EMIT', text)
    @classmethod
    def ARG(cls, argn, symbol): # NOSONAR
        return Instruction('ARG', argn, symbol)
    @classmethod
    def CONST(cls, value): # NOSONAR
        return Instruction('CONST', value)
    @classmethod
    def GET(cls, symbol): # NOSONAR
        return Instruction('GET', symbol)
    @classmethod
    def SET(cls, symbol): # NOSONAR
        return Instruction('SET', symbol)
    @classmethod
    def XCALL(cls, func): # NOSONAR
        return Instruction('XCALL', func)
    @classmethod
    def OUTFILE(cls): # NOSONAR
        return Instruction('OUTFILE')
    @classmethod
    def INCLUDE(cls, argc): # NOSONAR
        return Instruction('INCLUDE', argc)
    @classmethod
    def HALT(cls): # NOSONAR
        return Instruction('HALT')
    @classmethod
    def DUP(cls): # NOSONAR
        return Instruction('DUP')
    @classmethod
    def GETIDX(cls, arrreg, idxreg): # NOSONAR
        return Instruction('GETIDX', arrreg, idxreg)
    @classmethod
    def EVAL2(cls, op): # NOSONAR
        return Instruction('EVAL2', op)
    @classmethod
    def EVAL1(cls, op): # NOSONAR
        return Instruction('EVAL1', op)
    @classmethod
    def PRINT(cls): # NOSONAR
        return Instruction('PRINT')

    def __repr__(self) -> str:
        opcode = self.opcode
        arg1 = self.arg1
        arg2 = self.arg2
        if arg1:
            if arg2:
                return f"{opcode}({arg1},{arg2})"
            else:
                return f"{opcode}({arg1})"
        else:
            return f"{opcode}"

    @property
    def opcode(self):
        return self.op[0]

    @property
    def arg1(self):
        return self.op[1]

    @property
    def arg2(self):
        return self.op[2]

    def __repr__(self):
        arg1 = self.arg1
        arg2 = self.arg2
        result = " "*8
        if self.opcode == "LABEL":
            label = self.arg1+':'
            arg1 = None
            result = f"{label:7s} "
        elif self.opcode == 'CONST' or self.opcode == 'EMIT':
            if type(arg1) is str:
                arg1 = '"'+arg1.replace("\n",r"\n")+'"'

        result += self.opcode + " "
        if arg1 is not None:
            if arg2 is not None:
                result += f'{arg1}, {arg2}'
            else:
                result += f'{arg1}'
        return result

def print_program(prog):
    for i in prog:
        print(i)
