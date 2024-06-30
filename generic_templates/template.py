from typing import Optional, Dict, List

from .fpos import Fpos
from .template_vm import PreprocessorVM
from .template_parser import compile
from .template_secrets import find_replace_variables
from .error_report import ErrorReport


def preprocess(fp : Fpos, environ : dict={}, args : List[str]=[]) -> PreprocessorVM:
    """- Runs the preprocessor on the input file 'fp' and returns the result as a string
    Args:
        fp :Fpos: The file to be read from
        environ :Dict[str, str]: The initial environment defines
    """
    # Generate preprocessor script from input and execute the script in a VM
    vm = PreprocessorVM(environ, args)
    vm.prog(compile(fp))
    vm.execute()
    return vm

def fill_template(
        template_file :str,
        env : Dict[str, str],
        *argv,
        errors = None,
        fp :Optional[Fpos] = None
):
    """
    template_file :str: Path to the template file
    env :Dict[str,str]: Environment variables can be used in place of #define statements
    *argv :List[str]: Argument list
    errors :ErrorReport: 
    fp :Fpos: Optional open rewindable file input buffer with row and column position tracking
    Returns :str: The result of processing the template on success.  Throws an exception on error.
    """
    # read template
    #print(f"reading {template_file}")
    if '__FILE__' not in env:
        env['__FILE__'] = template_file
    if not fp:
        fp = Fpos(template_file)
    if errors is None:
        errors = ErrorReport()

    # process template
    vm = preprocess(fp, env, argv)
    body = find_replace_variables("".join(vm.output))
    errors.exit_on_error()
    
    # write output
    savepath = None
    if vm.outfile:
        savepath = vm.outfile
    elif template_file.endswith(".template"):
        savepath = template_file[:-9]

    if savepath:
        print(f"writing {savepath}")
        with open(savepath, "wt") as f:
            f.write(body)
    else:
        print(body)