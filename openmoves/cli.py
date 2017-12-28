"""
openmoves

Usage:
  openmoves online
  openmoves offline
  openmoves sample
  openmoves -h | --help
  openmoves --version

Options:
  -h --help                         Show this screen.
  --version                         Show version.

Examples:
  openmoves run
  openmoves sample
  
Help:
  If something doesn't work, tell Sam they're doing a bad job. 
"""

from inspect import getmembers, isclass
from docopt import docopt

def main():
    import openmoves.cmds
    options = docopt(__doc__, version='1')

    for (k, v) in options.items(): 
        if hasattr(openmoves.cmds, k) and v:
            module = getattr(openmoves.cmds, k)
            openmoves.cmds = getmembers(module, isclass)
            cmd = [cmd[1] for cmd in openmoves.cmds if cmd[0] != 'Base'][0]
            cmd = cmd(options)
            cmd.run()
