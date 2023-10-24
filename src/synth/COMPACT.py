import time
from datetime import datetime

from networkx import MultiDiGraph

from aux import config
from core.crossbars.Topology import Topology
from core.decision_diagrams.BDD import BDD
from synth.CrossbarMapping2D import CrossbarMapping2D
from synth.SynthesisMethod import SynthesisMethod
from synth.VHLabeling import VHLabeling


class COMPACT(SynthesisMethod):

    def __init__(self, bdd: BDD, layers: int = 1):
        """
        The class COMPACT initializes the framework.
        """
        super(COMPACT, self).__init__(bdd)
        self.layers = layers
        self.labeling = None

    def map(self) -> Topology:
        """
        Given a graph, and optionally a
        :return:
        """
        print("COMPACT started")
        print(datetime.now())
        self.start_time = time.time()
        # self.log += 'COMPACT version: {}\n'
        # self.log += 'Nodes: {}\n'.format(len(self.dd.dag.nodes))
        # self.log += 'Edges: {}\n'.format(len(self.dd.dag.edges))

        config.log.add('COMPACT version: VH-labeling\n')
        config.log.add('Gamma: {}\n'.format(config.gamma))
        config.log.add('Nodes: {}\n'.format(len(self.dd.dag.nodes)))
        config.log.add('Edges: {}\n'.format(len(self.dd.dag.edges)))
        vh_labeling = VHLabeling(self.dd.dag)
        self.labeling = vh_labeling.label()
        crossbar_mapping = CrossbarMapping2D(self.dd.dag)

        crossbar = crossbar_mapping.map(self.labeling)
        self.end_time = time.time()

        config.log.add('COMPACT time (s): {}\n'.format(self.end_time - self.start_time))

        print("COMPACT stopped")

        topology_graph = MultiDiGraph()
        topology_graph.add_node(crossbar)

        return Topology(topology_graph)

    def get_log(self) -> str:
        v, h, vh = VHLabeling.get_labels(self.labeling)
        log = ''
        log += 'Label V: {}\n'.format(v)
        log += 'Label H: {}\n'.format(h)
        log += 'Label VH: {}\n'.format(vh)
        # log += self.labeling.get_log()
        log += 'COMPACT time (s): {}\n'.format(self.end_time - self.start_time)
        # config.log_file.content += log
        return log
