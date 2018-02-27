import variables

class Supervised:
    """Supervised learning module"""

    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError("haven't moved stuff here, yet")
