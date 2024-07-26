from typing import Optional, Dict, List
import os

from .fpos import Fpos
from .template_instr import print_program
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
    prog = compile(fp)
    vm.prog(prog)
    vm.execute()
    return vm

def fix_module_names(fpath):
    from os.path import dirname, basename
    mydir = str(dirname(fpath))
    myfile = str(basename(fpath))
    if '.' in myfile:
        basefile, ext = myfile.rsplit(".", 1)
        myfile = f"{basefile.replace('.', '-')}.{ext}"
    return os.path.join(mydir, myfile)

def warning(templatepath, savepath):
    fname = os.path.basename(savepath)
    warning = """
#
# WARNING: This file was created automatically from the template located in:
#   __FILE__
# Any changes made here will be lost the next time the template is processed.
# Please update the template file to make durable changes.
#
"""
    ext=fname
    if '.' in fname:
        ext = fname.rsplit(".")[1]
    if ext in [ "py", "sh", "json", "Dockerfile", "yaml"]:
        cmt = "#"
    elif ext in [ "c", "cpp", "C", "java"]:
        cmt = "//"
    elif ext in [ "puml", "plantuml"]:
        cmt = "'"

    common_path = os.path.commonpath([templatepath, savepath])+"/"

    return warning.replace("#", cmt).replace("__FILE__", templatepath.replace(common_path,""))


def fill_template(
        template_file :str,
        env : Dict[str, str],
        *argv,
        errors = None,
        fp :Optional[Fpos] = None,
        output_dir :str = None,
        input_dir :str = None
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

    if input_dir:
        template_file = os.path.join(input_dir, template_file)
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
        if output_dir:
            if input_dir:
                savepath = savepath.replace(input_dir, output_dir)
            else:
                savepath = os.path.join(output_dir, savepath)
        savepath = fix_module_names(savepath) # removes illegal characters for python modules 
        odir = os.path.dirname(savepath)
        if odir and not os.path.isdir(odir):
            print(f"creating directory {odir}")
            os.makedirs(odir)
        

        print(f"writing {savepath}")

        with open(savepath, "wt") as f:
            f.write(warning(template_file, savepath))
            f.write(body)
    else:
        print(body)