def str_interpolate(template, kvlist={}):
    """ Replaces string contents with values from the kvlist
    """
    import re
    while True:
        m = re.search(r"\$([A-Za-z_]+)", template)
        if not m:
            m = re.search(r"\$({[A-Za-z_]+})", template)
        if not m:
            break
        var = "$"+m.group(1)
        #print(f"var={var}")
        if var in kvlist:
            #print(f"kvlist[var]={kvlist[var]}")
            template = template.replace(var, kvlist[var])
        else:
            raise ValueError(f"Unknown template variable {var}")
    return template