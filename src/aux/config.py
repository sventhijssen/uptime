import pathlib
import platform

from cli.ContextManager import ContextManager
from aux.Log import Log

context_manager = ContextManager()
log = Log()

# Settings for DD
time_limit_bdd = 60

# Settings for COMPACT
# Apply input and output constraints
io_constraints = True
# Apply a time limit
time_limit = None
# Keep auxiliary files from CPLEX
keep_files = False
# The gamma value
gamma = 1

record_formulae = False

root = pathlib.Path(__file__).parent.parent.parent.absolute()
abc_path = root.joinpath('abc')

if platform.system() == 'Windows':
    bash_cmd = ['bash', '-c']
    cplex_path = '/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x64_win64/cplex.exe'
elif platform.system() == 'Linux':
    bash_cmd = ['/bin/bash', '-c']
    cplex_path = '/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/cplex'
elif platform.system() == 'Darwin':
    bash_cmd = ['/bin/bash', '-c']
    cplex_path = '/Applications/CPLEX_Studio_Community2211/cplex/bin/x86-64_osx/cplex'
else:
    raise Exception("Unsupported OS: {}".format(platform.system()))

abc_cmd = bash_cmd.copy()
abc_cmd.extend(['"./abc"'])
abc_cmd = ' '.join(abc_cmd)

equivalence_checker_timeout = 3600
