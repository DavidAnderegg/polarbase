from matplotlib.axes._base import _AxesBase

class Plot(object):
    def __init__(self, axis: _AxesBase):
        self.axis = axis
