class template(object):
    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('this is a template')
