# generic_templates
Generates source files from templated source.  This tool is language agnostic.  You can use it as a preprocessor for python
code as easily as you can for XML, Yaml, JSON, or Java.  From the perspective of the preprocessor there are two types of 
information in a template, preprocessor instructions and anything else.  The anything else part gets copied to the output 
without change except that symbols that you define using the preprocessor instructions get interpolated into the output.

The generic template processor doesn't know anything about what your language considers to be a string, nor does it have 
any other way to avoid interpolation unless you choose preprocessor symbols that won't be confused with your targeted code.
As a result there is no need for the token pasting operator of the standard C preprocessor.  If you want your symbol to be
a string, just put string markers around it.

# Installation

```sh
  $ git clone <generic-templates>
  $ cd generic-templates
  $ pip install .
  $ keyring set aws <your-secrets>
```

# Library Usage

```python
  from generic_templates import fill_template
  env = { "@ENVIRON": "dev" }
  fill_template("myapplication.py.template", env)
```

# Fill-Template
The *generic_template* library includes a command line tool for processing generic template files using a language
that is similar in syntax to the C preprocessor.  The same functionality is also available in the library
by importing the 'fill_template' function from 'generic_template'.

Preprocessor symbols can be defined within the template by using the '#define' instruction, or from the command line
by using the '-D' option to define a symbol.  Preprocessor symbols can then be used to either include or skip over
other lines of code.  For example, in the code below the loglevel value assignment will be changed in the generated
output depending on whether the DEBUG preprocessor symbol is defined.

```bash
  $ fill-template -DDEBUG_LOGLEVEL=LogLevel.INFO foo.py.template
```

```python
  #define DEBUG
  #ifdef DEBUG
  logging.loglevel = DEBUG_LOGLEVEL
  #else
  logging.loglevel = LogLevel.ERROR
  #endif
```

A template can be initiated with a '#template' preprocessor instruction.  This identifies the number and order of
command line arguments for processing the template.  In the following example the fill-template command includes 
two additional command line parameters 't/bar' and 'data/raw/datasetname' which are loaded into the OUTFILE and DATASET
preprocessor symbols by the '#template' instruction.

```bash
  $ fill-template bar.py.template t/bar data/raw/datasetname
```

The '#define' on line 2 creates a new preprocessor symbol 'DSFILE' that contains only the basename 'datasetname' from the
full dataset path specified in 'DATASET'.  On line 3 the '#outfile' instruction changes the name of the python file that 
will be generated from the template.  The default is to remove the '.template' suffix from the template filename, but 
the outfile instruction calculates a new output filename by interpolating the string "OUTFILE_DSFILE.py", replacing 
any preprocessor symbols found in the string with their values, so the final output filename will be "t/bar_datasetname.py"
thus writing the template output to the 't' subdirectory below where the template is located.

```python
  #template OUTFILE, DATASET
  #define DSFILE basename(DATASET)
  #outfile interpolate("OUTFILE_DSFILE.py")
  from sparkle import transform_df, Input
  from pyspark.sql import functions as F
  @transform(
    df = Input("DATASET")
  )
  def compute(df):
    return df.withColumn(F.lit("DATASET"))
```

The '#halt' preprocessor instruction can be used to stop processing the template at that location and write the result.  This 
can be useful during debugging when you need to test the first half of a complex transform and stop at that point to check or run
the result so far.

```python
  from sparkle import transform_df, Input
  from pyspark.sql import functions as F
  @transform(
    df = Input("DATASET")
  )
  def compute(df):
    ... a lot of complex code ...
  #halt
    ... even more complex code ...
```

Repeating sections of code can be processed as templates by using the '#for' and '#endfor' preprocessor instructions.  Lines of code that
appear between those will iterate over the content repeating it as many times as there are items in an array contained within the variable
targeted by the for loop. An example of this is shown below:

```python
    #template @NLIST, @VLIST
    def func(
    #for @N, @V in @NLIST, @VLIST
        @N = @V,
    #endfor
    ):
        args = [
    #for @I, @N in indices(@NLIST), @NLIST
             ("@N", @N, @I),
    #endfor
        ]
        for n in args:
            print(f"{n[0]:32s} {n[1]}")
```
There is currenly no mechanism for building lists within the preprocessor language itself, so any lists that are
mapped to preprocessor variables must be delivered by code.  A sample invocation of the python template shown above can be seen in the
'test/foreach-test.py' file.

In the final pass after all of the preprocessor statements have been run, the 'fill-template' command will replace special symbols with 
known secrets.  The origin of the known secrets will vary depending on the type of secret and where the 'fill-template' command is running.
The supported secret types are:

```
  @settings.sh:<shell-var-name>@
  @env:<environment-variable>@
  @secret:<secret-id>@
```

Using 'settings.sh' the substitution will look for shell variable definitions in a file named 'settings.sh' in the current directory.
The environment variables must be defined in the form '<VARNAME>="<VALUE>"' to be eligible for substitution.  Interpolated shell 
variables are not supported.

Using 'env' the substitution will look for environment variables that are defined in the current process environment.

The supported values for 'secret-id' are listed in the SecretID enumeration within 'jupyter_aws.secretsmanager_client'.  Attempting to 
substitute a secret to which you don't have access will result in an error.  When running locally secret-id lookup will fetch the secret
from your local keyring where you can provide a development capable substitute secret.  When running in a local docker container the secret
will be fetched using the protocol supported by 'tiny-secret-server.py'.  When running in EKS the secret will be retrieved from the SecretsManager
service.  For this library the use of AWS SecretsManager has been stubbed out.

# Full Preprocessor Syntax

```
start: block

block: anyitem*

anyitem: body
    | condbody
    | include
    | define
    | instruction
    | foreach

foreach: FOREACH arglist IN exprlist block ENDFOREACH

?include: INCLUDE STRING -> include

define: DEFINE SYMBOL expr? -> setsymbol
    | TEMPLATE arglist -> template

arglist: SYMBOL
    | arglist COMMA SYMBOL

exprlist: expr -> exprlist
    | exprlist COMMA expr -> exprlist

instruction: HALT -> halt
    | OUTFILE expr -> outfile

condbody: IF bexpr block ENDIF -> condbody
    | IF bexpr block ELSE block ENDIF -> condbody
    | IFDEF SYMBOL block ENDIF -> condbody2
    | IFDEF SYMBOL block ELSE block ENDIF -> condbody2
    | IFNDEF SYMBOL block ENDIF -> condbody2

body: TEXT+

bexpr: expr COMP expr -> expr2
    | UNARY bexpr -> expr1
    | DEFINED LPAR SYMBOL RPAR -> expr1
    | bliteral -> expr0

bliteral: TRUE -> eval1
    | FALSE -> eval1

expr: SYMBOL -> eval1
    | STRING -> eval1
    | BASENAME LPAR expr RPAR -> fncall
    | DIRNAME LPAR expr RPAR -> fncall
    | INTERPOLATE LPAR expr RPAR -> fncall
    | INDICES LPAR expr RPAR -> fncall

%declare TEXT IF IFDEF IFNDEF ELSE ENDIF INCLUDE DEFINE SYMBOL ASSIGN STRING
%declare COMP UNARY DEFINED TRUE FALSE HALT TEMPLATE OUTFILE COMMA LPAR RPAR
%declare BASENAME DIRNAME INTERPOLATE IN FOREACH ENDFOREACH INDICES
```
