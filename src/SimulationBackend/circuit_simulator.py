from typing import Dict, Union, Literal, Tuple, List

from dotenv import load_dotenv

from components.general import GeneralComponent, componentDataType
from logger import logger
from .middleware import CircuitNode

from PySpice.Spice.Netlist import Circuit

load_dotenv()


componentsInfoType = Dict[
    str, Dict[Literal["data", "node1", "node2"], Union[componentDataType, str]]
]


class CircuitSimulator:
    def __init__(
        self,
        components: Dict[str, GeneralComponent],
        circuitNodes: Dict[str, CircuitNode],
    ) -> None:
        self.components = components
        self.circuitNodes = circuitNodes

        # keep track of ground nodes in the circuit
        self.GNDNodes: List[str] = []

        # extract component information from the components and nodes provided
        self.extractComponentNodesAndData()

    def extractComponentNodesAndData(self):
        logger.info("Extracting Components Information")
        self.componentsInfo: componentsInfoType = {}
        for component in self.components.values():
            # add the component data to componentsInfo
            componentInfo = {}
            componentInfo["data"] = component.data

            # get the two nodes the two terminals are connected to
            for circuitNode in self.circuitNodes.values():
                # check if currentNode is connected to a ground node
                if (
                    component.name == "GND"
                    and (component.uniqueID, 0) in circuitNode.componentTerminals
                ):
                    self.GNDNodes.append(circuitNode.uniqueID)
                if (component.uniqueID, 0) in circuitNode.componentTerminals:
                    componentInfo["node1"] = circuitNode.uniqueID
                if (component.uniqueID, 1) in circuitNode.componentTerminals:
                    componentInfo["node2"] = circuitNode.uniqueID

            # add single componentInfo to the full componentsInfo variable
            self.componentsInfo[component.uniqueID] = componentInfo

        logger.info("Components Information Extracted")
        return self.componentsInfo

    def createPySpiceCircuit(self):
        logger.info("Creating PySpice Circuit")
        # create an instance of the PySpice circuit
        circuit = Circuit("Circuit")
        # add circuit components based on the componentsInfo
        for componentID in self.componentsInfo.keys():
            componentInfo = self.componentsInfo.get(componentID)
            # get component's nodes
            node1 = (
                circuit.gnd
                if componentInfo.get("node1") in self.GNDNodes
                else componentInfo.get("node1")
            )
            node2 = (
                circuit.gnd
                if componentInfo.get("node2") in self.GNDNodes
                else componentInfo.get("node2")
            )
            if (node1 is not None) and (node2 is not None):
                if "Resistor" in componentID:
                    # component is a resistor. eg: Resistor-0
                    # add resistor component to the circuit instance
                    (R_value, R_unit) = componentInfo.get("data").get("R")
                    circuit.R(componentID, node1, node2, f"{R_value}@u_{R_unit}")
                    # adding current probe to the resistor to keep track of current flowing through resistor
                    circuit[f"R{componentID}"].plus.add_current_probe(circuit)
                elif "VoltageSource" in componentID:
                    # component is a voltage source. eg: VoltageSource-0
                    # add voltage source component to the circuit instance
                    (V_value, V_unit) = componentInfo.get("data").get("V")
                    circuit.V(componentID, node1, node2, f"{V_value}@u_{V_unit}")

        logger.info("PySpice Circuit Created")
        return circuit

    def simulate(self):
        logger.info("Simulating Circuit")
        # create a PySpice circuit instance with the component info
        circuit = self.createPySpiceCircuit()
        # create a simulator instance
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        # analyse the circuit
        try:
            analysis = simulator.operating_point()
        except:
            logger.exception("Operating point analysis failed.")
            return None

        # get the results from the analysis
        results = self.getResultsFromAnalysis(analysis)

        logger.info("Circuit Simulated.")

        return results

    def getResultsFromAnalysis(self, analysis) -> Dict[str, Dict[str, List[str]]]:
        results: Dict[str, Dict[str, List[str]]] = {}

        # get currents through all components from analysis
        currents: Dict[str, List[str]] = {}
        for current in analysis.branches.values():
            currentValue = float(current)
            componentName = str(current)
            currents[componentName] = [f"{currentValue:.4f}", "A"]

        # get voltages across all components and at all nodes from analysis
        voltages: Dict[str, List[str]] = {}
        for voltage in analysis.nodes.values():
            voltageValue = float(voltage)
            nodeName = str(voltage)
            voltages[nodeName] = [f"{voltageValue:.4f}", "V"]

        # combine current and voltage dictionaries into one big results dictionanry
        results["currents"] = currents
        results["voltages"] = voltages

        return results
