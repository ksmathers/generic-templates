import sys
from copy import copy

class Arglist:
    def __init__(self, *args):
        """
        Creates a shell style argument list with shift and shift_opts methods.  After calling
        shift_opts() any options will be available from the 'opt()' method.

        Example:
            va = Arglist(sys.argv[1:])
            va.shift_opts()
            cmd = va.shift()
            debug_flag = va.opt('debug', False)

        args :Alternative[List[str],List[List[str]]]: Construct from either an array or an argument list
        """
        if len(args) == 1 and type(args) is list:
            args = args[0]
        if args is None: 
            args = copy(sys.argv[1:]) # skip executable 
        self.opts = {}
        self.args = args

    def __len__(self):
        return len(self.args)
    
    def __getitem__(self, n:int) -> str:
        return self.args[n]
    
    @classmethod
    def help(cls):
        """Returns an Arglist containing just the word 'help' as an argument"""
        return cls('help')

    def _shift(self, default=None):
        arg = default
        if len(self.args)>0:
            arg = self.args[0]
            del self.args[0]
        return arg
    
    def _peek(self):
        arg = None
        if len(self.args)>0:
            arg = self.args[0]
        return arg

    def shift_all(self, specials=[]):
        """ - returns the remaining arguments joined with spaces as a single string
        specials : a list of strings that need to be quoted
        """
        p = [ '"' + x.replace("\"","\\\"") + '"' 
              if any(special in x for special in specials)
              else x 
              for x in self.args ]
        self.args=[]
        return ' '.join(p)
        
    def shift(self, default=None):
        #self.shift_opts()
        return self._shift(default)
    
    def stack_opts(self, options : str):
        arg =  self._peek()
        while arg and len(arg)==2 and arg[0]=='-':
            #print(arg, '/', self.args)
            self._shift()
            opt = arg[1]
            optarg = options.find(opt)
            if optarg < 0:
                raise ValueError(f"Invalid option -{opt}")
            param = True
            #print("arg", arg, "optarg", optarg, "param") #, options[optarg+1])
            if len(options)>optarg+1 and options[optarg+1]==':':
                param=self._shift()
            if opt not in self.opts:
                self.opts[opt] = []
            self.opts[opt].append(param)
            arg = self._peek()

    def shift_opts(self):
        while len(self.args)>0 and self.args[0].startswith('-') and self.args[0] != '-':
            opt = self._shift()[1:]
            if opt == '--': 
                break
            if opt.startswith('-'):
                opt = opt[1:]
            if '=' in opt:
                opt, optval = opt.split('=',1)
            else:
                optval = True
            self.opts[opt]=optval

    def opt(self, optname, default=None):
        return self.opts.get(optname, default)

