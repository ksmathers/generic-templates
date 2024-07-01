from generic_templates import fill_template, Fpos
import generic_templates

#generic_templates.template_parser.TRACE = True
#generic_templates.template_tokenizer.TRACE = True
#generic_templates.template_vm.TRACE = True



fp = Fpos.from_string("""
#template @NLIST, @VLIST
def func(
#for @N, @V in @NLIST, @VLIST
    @N = @V,
#endfor
):
    args = [
#for @I, @N in indices(@NLIST), @NLIST
        ("@N", @N),    # args[@I]
#endfor
    ]
    for n in args:
        print(f"{n[0]:32s} {n[1]}")
""")

fill_template("output-foreach-test.py.template", {}, ['a', 'b', 'c'], [1, 2, 3], fp=fp)