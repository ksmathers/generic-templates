import re
try:
    from jupyter_aws.secret import Secret
except:
    from .secret import Secret
from .error_report import ErrorReport

def replace_variable(body, span, varvalue):
    """- Global string replacement in the body of a document
    Args:
        body :str: The document being changed
        span :str: The text that was detected as replaceable
        varvalue :str: Replacement for the span
    """
    #print(f"replace_variable(body..., {span}, {varvalue})")
    if varvalue is None:
        varvalue = "NODATA"
    body = body.replace(span, varvalue)
    #print(body)
    return body

def get_secret(varname : str) -> str:
    """- Fetches a secret by name
    Args:
        varname :str: The name of the secret to fetch the value of
    Returns:
        :str: the value of the secret
    """

    varvalue = None
    try:
        secretid = Secret(varname)
        varvalue = secretid.get_secret()
        if varvalue is None:
            raise ValueError(f"invalid secret {varname}")
    except AttributeError:
        errors.error(f"Value error: Unable to get secret '{varname}'")

    #print("get_secret", varname, "->", varvalue)
    return varvalue


settings = None
def get_setting(varname : str) -> str:
    """- Returns an entry from a shell script 'setting.sh' in your local directory

    The file 'setting.sh' must contain shell variable definitions in the format:
        VARNAME="<value>"
    Any lines that do not have that format are ignored.

    Args:
        varname :str: The name of the setting to fetch
    Returns:
        :str: the value of the shell variable (ie the dequoted string)
    """
    global settings
    if settings is None:
        with open("setting.sh", "rt") as f:
            settings = {}
            for line in f.readlines():
                m = re.match(r'^ *([A-Za-z][A-Za-z0-9]*)="(.*)"$', line)
                if m:
                    var = m.group(1)
                    val = m.group(2)
                    print(f"Setting {var}={val}")
                    settings[var] = val
    return settings[varname]


def find_replace_variables(body : str) -> str:
    """- Interpolates variables in the body of a document

    Variables have the form '@<type>:<varname>[.<property>]@'.  The supported
    values for <type> are:
       - secret: fetches a secret from keyring or AWS SecretsManager depending on environment
       - env: fetches an environment variable
       - setting.sh: fetches a shell variable from 'setting.sh' in local directory

    The <varname> part must match the name of a secret in the current runtime
    environment.

    Args:
        body :str: The document body to be interpolated.
    """
    while True:
        m = re.search(r"@([a-zA-Z_\.-]+):([a-zA-Z_\.-]+)@", body)
        if m:
            span = m.group(0)
            vartype = m.group(1)
            varname = m.group(2)
            #print(f"find_replace_variables: {vartype} {varname}")
            if vartype == "secret":
                varname, varprop = varname.split(".")
                varvalue = get_secret(varname)[varprop]
            elif vartype == "env":
                varvalue = os.environ.get(varname)
                if varvalue is None:
                    errors.error(f"Value error: Unable to get env '{varname}'")
            elif vartype == "setting.sh":
                varvalue = get_setting(varname)
            else:
                errors.error(f"Unknown variable type: '{vartype}'")
                varvalue = None
            body = replace_variable(body, span, varvalue)
        else:
            break
    return body