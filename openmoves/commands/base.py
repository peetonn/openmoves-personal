class Base(object):
    """A template command"""
    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('This is a template')
