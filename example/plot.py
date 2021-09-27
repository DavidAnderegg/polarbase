# from polarbase.plots import
from polarbase import PolarBase


pb = PolarBase('data')


pb.Plots.polar(
        [
            pb.Airfoil.n0021,
                ],
        solver=[
            pb.Solver.SU2,
            ],

        )
