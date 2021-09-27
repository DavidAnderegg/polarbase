from matplotlib.axes._base import _AxesBase

from polarbase.plots import Plot


class simpleAerodynamicPolarPlot(Plot):
    def __init__(self, axis: _AxesBase):
        super().__init__(axis)
