from template import .template

class offline(template):
    """Offline analyses of OPT data. Will probably be broken up into
    several different CL commands, instead"""

    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError("haven't moved stuff here, yet")
