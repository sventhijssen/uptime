import os
from pathlib import Path

from aux import config
from aux.BivariateGaussianDefectCrossbarGenerator import BivariateGaussianDefectCrossbarGenerator
from aux.DataLayoutReorganization import DataLayoutReorganization
from cli.Program import Program

benchmark_name = "misex1"
bdd = "sbdd"

current_path = Path(os.getcwd())

log_filename = benchmark_name + ".log"
log_filepath = current_path.joinpath(log_filename)

benchmark_filename = benchmark_name + ".pla"
benchmark_filepath = current_path.joinpath(benchmark_filename)

xbar_filename = benchmark_name + ".xbar"
xbar_filepath = current_path.joinpath(xbar_filename)

generator = BivariateGaussianDefectCrossbarGenerator(128, 128, 0.01)
crossbar = list(generator.generate(1))[0]

program = Program()
Program.execute("new_log {} | read {} | {} | compact | write_xbar {}".format(log_filepath, benchmark_filepath, bdd, xbar_filepath))

# This must be cleaner in the future, but this is how you can obtain your crossbar design.
ctx = config.context_manager.get_context()
topology = list(ctx.boolean_functions)[0]
sub_topology = list(topology.graph.nodes)[0]
design = list(sub_topology.graph.nodes)[0]

data_layout_reorganization = DataLayoutReorganization(design, crossbar)
mapped_design = data_layout_reorganization.map()
