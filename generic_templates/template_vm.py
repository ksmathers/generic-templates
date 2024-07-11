import sys
import os
from .arglist import Arglist

from .template_instr import Instruction

TRACE=False


class PreprocessorVM:
    def __init__(self, env=None, argv:Arglist=None):
        """ The preprocessor VM is a simple stack machine with no registers.  Instead all instructions
        run either the top of the stack or using one of the two arguments present in the instruction
        itself.  There is also indexed memory for storing and retrieving variables (self.vars).

        There is also a jump table (self.labels) used to move the PC to the correct instruction when
        branching.  Labels are initialized by prescanning the code for 'LABEL' instructions.

        Note: The '#include' preprocessor instruction is currently unimplemented.  Making it work would
        require pushing the current context, parsing the imported file into a new program, then executing
        the new program until it exits before restoring the current context.
        """
        if env is None:
            env = {}
        self.stack = []
        self.vars = env
        self.progmem = [ Instruction.LABEL('main') ]
        self.pc = 0
        self.seg_count = 0          # generates unique labels
        self.output = []
        self.outfile = None
        self.running = False
        self.labels = {}
        self.r = { f'R{x}': None for x in range(64) }
        self.argv = argv or Arglist()
        self.scan_labels()

    def get_r(self, reg):
        assert(reg in self.r)
        return self.r[reg]

    def set_r(self, reg, value):
        assert(reg in self.r)
        self.r[reg] = value

    def scan_labels(self):
        """ Scans program memory for LABEL statements and adds them to the index """
        for pc,i in enumerate(self.progmem):
            if i.opcode == 'LABEL':
                self.labels[i.arg1] = pc

    def prog(self, instr):
        """ Appends a new program to progmem and rescans the labels """
        self.progmem.extend(instr)
        if TRACE:
            from .template_instr import print_program
            print_program(self.progmem)
        self.scan_labels()

    def gensym(self):
        """ Generates a unique LABEL symbol """
        self.seg_count += 1
        return f"SEG_{self.seg_count:03d}"

    def push(self, v):
        """ Data stack push """
        self.stack.append(v)

    def pop(self):
        """ Data stack pop, exception on underflow """
        v = self.stack[-1]
        del self.stack[-1]
        return v

    def interpolate(self, body:str):
        """Interpolates preprocessor variables into the string given, starting with the longest strings to allow for the possibility
        of common prefixes in variable names.

        body :str: Body of text within which to interpolate variables
        """
        for v in sorted(self.vars, key=len, reverse=True):
            val = str(self.vars[v])
            body = body.replace(v, val)
        return body

    def execute1(self):
        """ Executes a single instruction in the Preprocessor VM
        """
        if not self.running: return

        pc = self.pc
        instr = self.progmem[pc]
        if TRACE:
            print(f"{pc:03d} {instr}")
            print("  v", self.vars)
            print("  s", self.stack)
        opcode = instr.opcode
        arg1 = instr.arg1
        arg2 = instr.arg2
        pc += 1
        self.pc = pc
        if opcode == 'EMIT':
            self.output.append(self.interpolate(arg1))
        elif opcode == 'GET':
            self.push(self.vars.get(arg1,''))
        elif opcode == 'CONST':
            self.push(arg1)
        elif opcode == 'DUP':
            self.push(self.stack[-1])
        elif opcode == 'EVAL2':
            cond = arg1
            a = self.pop()
            b = self.pop()
            if cond == '==':
                v = (a == b)
            elif cond == '<=':
                v = (a <= b)
            elif cond == '>=':
                v = (a >= b)
            elif cond == '<':
                v = (a < b)
            elif cond == '>':
                v = (a > b)
            elif cond == '!=':
                v = (a != b)
            self.push(v)
        elif opcode == 'EVAL1':
            cond = arg1
            a = self.pop()
            if cond == '!':
                v = not a
            elif cond == 'defined':
                v = (a in self.vars)
            self.push(v)
        elif opcode == 'JMPIF':
            cond = self.pop()
            lbl = arg1
            if cond:
                self.pc = self.labels[lbl]
        elif opcode == 'JMP':
            lbl = arg1
            self.pc = self.labels[lbl]
        elif opcode == 'SET':
            var = arg1
            val = self.pop()
            self.vars[var] = val
        elif opcode == 'ARG':
            # ARG number, var
            number = arg1
            var = arg2
            assert(type(number) is int)
            assert(type(var) is str)
            assert(number < len(self.argv)), "Template is asking for more arguments than were given"
            self.vars[var] = self.argv[number]
        elif opcode == 'OUTFILE':
            # OUTFILE [arglist]
            assert('__FILE__' in self.vars)
            basedir = os.path.dirname(self.vars['__FILE__'])
            filename = self.pop()
            assert(not filename.startswith("/"))
            self.outfile = os.path.join(basedir, filename)
        elif opcode == 'INCLUDE':
            raise NotImplementedError("Not implemented INCLUDE")
        elif opcode == 'PRINT':
            # PRINT
            print(self.pop())
        elif opcode == 'HALT':
            self.running = False
        elif opcode == 'XCALL':
            # XCALL <function>
            if arg1 == 'basename':
                self.push(os.path.basename(self.pop()))
            elif arg1 == 'dirname':
                self.push(os.path.dirname(self.pop()))
            elif arg1 == 'interpolate':
                self.push(self.interpolate(self.pop()))
            elif arg1 == 'len':
                self.push(len(self.pop()))
            elif arg1 == 'indices':
                self.push(list(range(len(self.pop()))))
        elif opcode == 'EXISTS':
            sym = arg1
            self.push(sym in self.vars)
        elif opcode == 'LABEL':
            pass #NOSONAR
        elif opcode == 'FATAL':
            msg = arg1
            print(msg, file=sys.stderr)
            sys.exit(1)
        elif opcode == 'PUSH':
            reg = arg1
            self.push(self.get_r(reg))
        elif opcode == 'POP':
            reg = arg1
            self.set_r(reg, self.pop())
        elif opcode == 'ADD':
            reg = arg1
            const = arg2
            self.set_r(reg, self.get_r(reg)+const)
        elif opcode == 'GETIDX':
            arrreg = arg1
            idxreg = arg2
            self.push(self.get_r(arrreg)[self.get_r(idxreg)])

    def execute(self):
        """ Executes the preprocessor program that was built from parsing a template file
        """
        self.pc = self.labels['main']
        self.running = True
        while (self.running):
            try:
                self.execute1()
            except Exception as e:
                print(self.pc, str(e))
                raise e