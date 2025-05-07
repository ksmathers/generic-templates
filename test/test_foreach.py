from multicloud.generic_templates import fill_template, Fpos
from multicloud import generic_templates

#generic_templates.template_parser.TRACE = True
#generic_templates.template_tokenizer.TRACE = True
#generic_templates.template_vm.TRACE = True

def test_foreach():
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

    fill_template("output-foreach-test.py.template", {}, ['a', 'b', 'c'], [1, 2, 3], fp=fp, input_dir="/tmp", output_dir="/tmp")
    success_result = """
#
# WARNING: This file was created automatically from the template located in:
#   output-foreach-test.py.template
# Any changes made here will be lost the next time the template is processed.
# Please update the template file to make durable changes.
#

def func(
    a = 1,
    b = 2,
    c = 3,
):
    args = [
        ("a", a),    # args[0]
        ("b", b),    # args[1]
        ("c", c),    # args[2]
    ]
    for n in args:
        print(f"{n[0]:32s} {n[1]}")

"""
    with open("/tmp/output-foreach-test.py", "rt") as f:
        actual_result = f.read()
    assert(actual_result == success_result)

if __name__ == "__main__":
    test_foreach()