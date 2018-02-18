"""
openmoves

Usage:
  openmoves readin
  openmoves sample
  openmoves -h | --help
  openmoves --version

Options:
  readin                            Run OpenMoves with options as configured in config.json
  sample                            Run OpenMoves with sample simulator
  -h --help                         Show this screen
  --version                         Show version

Examples:
  openmoves readin
  openmoves sample
  
Help:
  If something doesn't work, tell Sam they're doing a bad job. 
"""

from inspect import getmembers, isclass
from docopt import docopt

from . import __version__ as VERSION

def main():
    import openmoves.commands
    options = docopt(__doc__, version=VERSION)

    for (k, v) in options.items(): 
        if hasattr(openmoves.commands, k) and v:
            module = getattr(openmoves.commands, k)
            openmoves.commands = getmembers(module, isclass)
            command = [command[1] for command in openmoves.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
