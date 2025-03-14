

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
