from lark.lexer import Lexer, Token
import re
TRACE=False

class PreprocessorLexer(Lexer):
    """Tokenizes an input file returning TEXT tokens for unrecognized text, and preprocessor
    tokens for C preprocessor instructions.  Whitespace is ignored by the lexical analyzer except
    that it resets the state to rules0"""
    rules0 = [
        ("INCLUDE", r"^#[ ]*include\b"),
        ("TEMPLATE", r"^#[ ]*template\b"),
        ("DEFINE", r"^#[ ]*define\b"),
        ("IFDEF", r"^#[ ]*ifdef\b"),
        ("IFNDEF", r"^#[ ]*ifndef\b"),
        ("IF", r"^#[ ]*if\b"),
        ("ELSE", r"^#[ ]*else\b"),
        ("ENDIF", r"^#[ ]*endif\b"),
        ("HALT", r"^#[ ]*halt\b"),
        # ("ARG", r"^#[ ]*arg\b"),
        ("OUTFILE", r"^#[ ]*outfile\b"),
        ("FOREACH", r"^#[ ]*for\b"),
        ("ENDFOREACH", r"^#[ ]*endfor\b")
    ]

    rules1 = [
        ("TRUE", r"\btrue\b"),
        ("FALSE", r"\bfalse\b"),
        ("SPACE", r"[\t ]+"),
        ("COMP", r"(==|<=|>=|<|>)"),
        ("UNARY", r"!"),
        ("ASSIGN", r"="),
        ("DEFINED", r"\bdefined\b"),
        ("BASENAME", r"\bbasename\b"),
        ("DIRNAME", r"\bdirname\b"),
        ("INTERPOLATE", r"\binterpolate\b"),
        ("INDICES", r"\bindices\b"),
        ("IN", r"\bin\b"),
        ("LPAR", r"\("),
        ("RPAR", r"\)"),
        ("COMMA", r","),
        ("SYMBOL", r"[@A-Za-z_][@A-Za-z0-9_]*"),
        ("STRING", r'"[^"]*"'),
        ("EOL", r"\n"),
    ]

    def __init__(self, lexer_conf=None):
        """- Construct PreprocessorLexer"""
        pass

    def next_token(self, fp):
        """- Fetch the next token"""
        global TRACE
        if fp.eof:
            if TRACE: print("+EOF+")
            return None
        if fp.cpos == 0:
            for r,pat in self.rules0:
                m = re.match(pat, fp.v)
                #print("next_token:", m, pat, fp.v)
                if m:
                    token = Token(r, m.group(0), 0, fp.rpos, fp.cpos)
                    fp.skip(len(token.value))
                    if TRACE: print(f"+TOKEN+ {token.type:16s} {token.value}")
                    return token
            ltext = fp.v
            if not ltext.endswith('\n'):
                ltext += '\n'
            token = Token("TEXT", ltext, 0, fp.rpos, fp.cpos)
            fp.skip(len(fp.v))
            if TRACE: print(f"+TOKEN+ {token.type:16s} {token.value}")
            return token
        else:
            for r,pat in self.rules1:
                m = re.match(pat, fp.v)
                if m:
                    token = Token(r, m.group(0), 0, fp.rpos, fp.cpos)
                    fp.skip(len(token.value))
                    if TRACE: print(f"+TOKEN+ {token.type:16s} {token.value}")
                    return token
            raise TypeError(f"Invalid token at {fp.v}")

    def lex(self, fp):
        """- Generates tokens until EOF.  Whitespace tokens are skipped.
        Args:
          fp :Fpos: The input stream to read from
        """
        while True:
            tok = self.next_token(fp)
            if tok is None:
                break
            #print(f"{tok.type:16s} {tok.value}")
            if not (tok.type == 'SPACE' or tok.type == 'EOL'):
                yield tok