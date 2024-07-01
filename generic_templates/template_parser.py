from lark import Transformer, Lark
from .template_instr import Instruction, gensym
from .template_tokenizer import PreprocessorLexer
import sys

TRACE=False

# Syntax definition for the preprocessor
preprocessor_bnf = r"""
start: block

block: anyitem*

anyitem: body
    | condbody
    | include
    | define
    | instruction
    | foreach

foreach: FOREACH arglist IN exprlist block ENDFOREACH

?include: INCLUDE STRING -> include

define: DEFINE SYMBOL expr? -> setsymbol
    | TEMPLATE arglist -> template

arglist: SYMBOL
    | arglist COMMA SYMBOL

exprlist: expr -> exprlist
    | exprlist COMMA expr -> exprlist

instruction: HALT -> halt
    | OUTFILE expr -> outfile

condbody: IF bexpr block ENDIF -> condbody
    | IF bexpr block ELSE block ENDIF -> condbody
    | IFDEF SYMBOL block ENDIF -> condbody2
    | IFDEF SYMBOL block ELSE block ENDIF -> condbody2
    | IFNDEF SYMBOL block ENDIF -> condbody2

body: TEXT+

bexpr: expr COMP expr -> expr2
    | UNARY bexpr -> expr1
    | DEFINED LPAR SYMBOL RPAR -> expr1
    | bliteral -> expr0

bliteral: TRUE -> eval1
    | FALSE -> eval1

expr: SYMBOL -> eval1
    | STRING -> eval1
    | BASENAME LPAR expr RPAR -> fncall
    | DIRNAME LPAR expr RPAR -> fncall
    | INTERPOLATE LPAR expr RPAR -> fncall
    | INDICES LPAR expr RPAR -> fncall

%declare TEXT IF IFDEF IFNDEF ELSE ENDIF INCLUDE DEFINE SYMBOL ASSIGN STRING
%declare COMP UNARY DEFINED TRUE FALSE HALT TEMPLATE OUTFILE COMMA LPAR RPAR
%declare BASENAME DIRNAME INTERPOLATE IN FOREACH ENDFOREACH INDICES
"""

# Utility functions
def unwrap_str(s):
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s


# Parser tree transformer to output file (as a list of lines)
class ParsePreprocessor(Transformer):
    def __init__(self):
        pass

    def log(self, node, v):
        global TRACE
        if TRACE:
           print(f"reduce {node} {v}", file=sys.stderr)

    def start(self, v):
        # block
        self.log("start",v)
        block = v[0]
        result = block + [
            Instruction.HALT()
        ]
        return result

    def dumpstack(self, rule, v):
        print(rule, "dumpstack")
        for i, iv in enumerate(v):
            print(f"  {i:02d} - {iv}")

    def foreach(self, v):
        #self.dumpstack("foreach",v)
        # FOREACH arglist IN exprlist block ENDFOREACH
        arglist = v[1]
        exprlist = v[3]
        block = v[4]
        assert(len(arglist)==len(exprlist))

        arglen = len(arglist)

        # save the registers that will be used for this foreach loop and initialize the main index
        code = [
            Instruction.PUSH(f'R{n}') for n in range(arglen+2)
        ] + [
            Instruction.CONST(0),
            Instruction.POP('R0'),   # index
        ]

        # initialize the lists that will be iterated over
        for i in range(len(arglist)):
            code += exprlist[i]                     # run the n-th expr
            if i==0:
                code += [
                    Instruction.DUP(),
                    Instruction.XCALL('len'),
                    Instruction.POP('R1')        # len of first expr is saved in R1
                ]
            code += [
                Instruction('POP', f"R{i+2}")       # n-th expr result
            ]

        # check if we are at the end of the loop iterations
        loop0 = gensym('loop')
        break0 = gensym('brk')
        code += [
            Instruction.LABEL(loop0),
            Instruction.PUSH('R0'),
            Instruction.PUSH('R1'),
            Instruction.EVAL2('<='),
            Instruction.JMPIF(break0),           # exit loop if len <= index
        ]

        # set the iterators
        for i in range(len(arglist)):
            code += [
                Instruction.GETIDX(f'R{i+2}', 'R0'),
                Instruction.SET(arglist[i])      # arglist[i] = expr[i]
            ]

        # run the loop body, increment, and loop.  on loop exit restore the registers.
        code += block + [
            Instruction.ADD('R0', 1),
            Instruction.JMP(loop0),
            Instruction.LABEL(break0) #end
        ] + [
            Instruction.POP(f'R{n-1}') for n in range(arglen+2, 0, -1)
        ]
        return code


    def block(self, v):
        # anyitem*
        self.log("block", v)
        result = []
        for i in v:
            result.extend(i)
        return result

    def template(self, v):
        # TEMPLATE arglist
        self.log("template", v)
        result = [
            Instruction.EMIT("""
#
# WARNING: This file was created automatically from the template located in:
#   __FILE__
# Any changes made here will be lost the next time the template is processed.
# Please update the template file to make durable changes.
#
""")]
        for i, _v in enumerate(v[1]):
            result.append(Instruction.ARG(i, _v))
        return result

    def arglist(self, v):
        # symbol | arglist, symbol
        self.log("arglist", v)
        if len(v)==1:
            result = [ v[0].value ]
        else:
            result = v[0] + [ v[2].value ]
        return result

    def exprlist(self, v):
        #self.dumpstack("exprlist", v)
        # expr | exprlist, expr
        self.log("exprlist", v)
        if len(v)==1:
            result = [ v[0] ]
        else:
            v[0].append(v[2])
            result = v[0]
        return result

    def halt(self, v):
        # halt
        self.log("halt", v)
        return [ Instruction.HALT() ]

    def outfile(self, n):
        # outfile string
        self.log("outfile", n)
        return n[1] + [ Instruction.OUTFILE() ]

    def anyitem(self, v):
        self.log("anyitem", v)
        return v[0]

    def setsymbol(self, v):
        self.log("setsymbol", v)
        var = v[1].value
        value = True
        if len(v) > 2:
            value = v[2]
        else:
            value = [ Instruction.CONST(True) ]

        result = value + [
            Instruction.SET(var)
        ]

        #print(f"node setsymbol  {result}", file=sys.stderr)
        return result

    def body(self, v):
        self.log("body", v)
        result = [ Instruction.EMIT(x.value) for x in v ]
        return result

    def condbody(self, v):
        self.log("condbody", v)
        bexpr = v[1]
        truestart = v[2]
        falsestart = v[4] if len(v)==6 else []

        # if bcond truestart else falsestart endif
        truecase = gensym('true')
        xcontinue = gensym('xcont')
        result = bexpr + [
            Instruction.JMPIF(truecase)
        ] + falsestart + [
            Instruction.JMP(xcontinue),
            Instruction.LABEL(truecase)
        ] + truestart + [
            Instruction.LABEL(xcontinue)
        ]

        #print(f"node condbody -> {result}", file=sys.stderr)
        return result

    def condbody2(self, v):
        self.log("condbody2", v)
        sym = v[1].value

        truestart = v[2]
        falsestart = v[4] if len(v)==6 else []

        # ifn?def sym block1 else block2 endif
        truecase = gensym('true')
        xcontinue = gensym('xcont')

        invert = []
        if v[0].type == 'IFNDEF':
            invert = [ Instruction.EVAL1('!') ]

        result = [
            Instruction.CONST(sym),
            Instruction.EVAL1('defined')
        ] + invert + [
            Instruction.JMPIF(truecase)
        ] + falsestart + [
            Instruction.JMP(xcontinue),
            Instruction.LABEL(truecase)
        ] + truestart + [
            Instruction.LABEL(xcontinue)
        ]

        #print(f"node condbody2 -> {result}", file=sys.stderr)
        return result

    def fncall(self, n):
        # returns a list of instructions
        # <function> ( <expr> )

        self.log("fncall", n)

        builtin = n[0].type
        return n[2] + [ Instruction.XCALL(builtin.lower()) ]

    def eval1(self, n):
        # returns a list of instructions
        self.log("eval1", n)
        cond = n[0].value
        if n[0].type == 'SYMBOL':
            return [ Instruction.GET(cond) ]
        elif n[0].type == 'STRING':
            return [ Instruction.CONST(unwrap_str(cond))]
        elif n[0].type == 'TRUE':
            return [ Instruction.CONST(True)]
        elif n[0].type == 'FALSE':
            return [ Instruction.CONST(False)]
        raise NotImplementedError(f"eval1: Type {n[0].type}")

    def expr0(self, v):
        self.log("expr0", v)
        result = v[0]
        return result

    def expr1(self, v):
        self.log("expr1", v)
        if v[0].type == 'UNARY':
            # ! a
            a = v[1]
            func = v[0].value
        elif v[0].type == 'DEFINED':
            # defined ( a )
            a = v[2]
            func = 'defined'

        result = a + [ Instruction.EVAL1(func) ]
        #print(f"node expr1 {result}", file=sys.stderr)
        return result

    def expr2(self, v):
        # a <=> b
        self.log("expr2", v)
        a = v[0]
        cmp = v[1].value
        b = v[2]
        result = b + a + [ Instruction.EVAL2(cmp) ]
        #print(f"node expr2 {result}", file=sys.stderr)
        return result


def compile(fp):
    # Generate preprocessor script from input and execute the script in a VM
    parser = Lark(preprocessor_bnf, parser='lalr', lexer=PreprocessorLexer)
    try:
        tree = parser.parse(fp)
    except Exception as e:
        print(e)
        sys.exit(1)
    #print(tree)
    program = ParsePreprocessor().transform(tree)
    return program