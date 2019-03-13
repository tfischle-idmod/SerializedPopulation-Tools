import sys
sys.path.append("C:\\Users\\tfischle\\Github\\DtkTrunk_master\\Scripts\\serialization")
import dtkFileTools as dft
import dtkFileSupport as support
import random
import matplotlib.pyplot as plt
import utils
import json
import scipy.stats
import collections
import pathlib
import difflib
import copy



counter =0
nextInfectionSuid_initialized = False
nextInfectionSuid_suid = None
dtk = None

class dtk_class:

    def __init__(self, file):
        self.nextInfectionSuid_suid = None
        self.nextInfectionSuid_initialized = False
        self.dtk = dft.read(file)
        self._nodes = [n for n in self.dtk.nodes]

    def get_node(self):
        return self._nodes

    nodes = property(get_node)

    def close(self):
        for idx in range(len(self._nodes)):
            self.dtk.nodes[idx] = self._nodes[idx]

    def write(self):
        sim = self.dtk.simulation
        sim["infectionSuidGenerator"]['next_suid']['id'] = self.getNextInfectionSuid()
        self.dtk.simulation = sim

        self.dtk.compression = dft.NONE
#        self.dtk.compressed = False
        dft.write(self.dtk, "my_dtk_file.dtk")

    def getNextInfectionSuid(self):
        sim = self.dtk.simulation
        if not self.nextInfectionSuid_initialized:
            self.nextInfectionSuid_suid = sim["infectionSuidGenerator"]['next_suid']
            self.nextInfectionSuid_initialized = True
        else:
            self.nextInfectionSuid_suid['id'] = self.nextInfectionSuid_suid['id'] + sim["infectionSuidGenerator"]['numtasks']

        return self.nextInfectionSuid_suid

    def getNextIndividualSuid(self, node_id):
        suid = self._nodes[node_id]["m_IndividualHumanSuidGenerator"]['next_suid']
        self._nodes[node_id]["m_IndividualHumanSuidGenerator"]['id'] = suid['id'] + self._nodes[node_id]["m_IndividualHumanSuidGenerator"]['numtasks']
        return suid['id']



def removeIndividuals(node_id, number_of_ind, handle):
    node = handle.nodes[node_id]
    del node.individualHumans[0:number_of_ind]


def changeSusceptibility(node_id, number_of_ind, properties, handle):
    node = handle.nodes[node_id]
    for num in range(0,number_of_ind):
        for prop in properties:
            node.individualHumans[num].susceptibility[prop] = properties[prop]


def setIndividualPropertyInfections(node_id, individual_idx, prop_value, handle):
    node = handle.nodes[node_id]
    for idx in individual_idx:
        for prop in prop_value:
            node['individualHumans'][idx]['infections'][0][prop] = prop_value[prop]


def generatePopulation(prop_values, node, copy_ind):
    #copy_ind = dtk_obj.nodes[0].individualHumans[0]
    for individual_props in prop_values:
        ind = createIndividual("Generic", node.getNextIndividualSuid(0), copy_ind=copy_ind, kwargs=individual_props)
        node.individualHumans.append(ind)


def setIndividualProperty(node_id, individual_idx, prop_value, handle):
    """change key value of some individual properties, given as a list of indices."""
    for idx in individual_idx:
        for prop in prop_value:
            handle.nodes[node_id]['individualHumans'][idx][prop] = prop_value[prop]


def setPropertyValues_Individual(node_id, param_value, handle):
    """ length of param_value must be equal to number of individuals.
     Every entry in paramvalue is a dict wit one or several key-value pairs."""
    for param, ind in zip(param_value, handle.nodes[node_id]['individualHumans']):
        ind.update(param)


def getPropertyValues_Individual(node_id, handle, property):
    """returns list values for property property or if the property is a list, the length of the list"""
    if handle:
        node = handle.nodes[node_id]
        return [ind[property] for ind in node.individualHumans]
    return None


def getIndividualsWithProperty(handle, fct=lambda ind: True):
    """ get all individuals that fulfill a certain condition. Condition is given by fct."""
    individuals = handle.individualHumans
    return [ind for ind in individuals if fct(ind)]


def createInfection(type, suid, kwargs={}):
    infection = None
    if type == "Generic":   # make dependant in sim type?
        with open("infection.json", "r") as file:
            infection = json.load(file)
    elif type == "Malaria":
        pass
    else:
        print("Infection of type" + type + " does not exist")

    infection["suid"] = suid
    infection.update(kwargs.items())

    return infection


def addInfectionToIndividuals_fct(handle, infection, fct=lambda ind: True):
    """Add infection to individuals that fulfill a certain criteria e.g. age"""
    add(handle["individualHumans"], "infections", infection, fct)


def createIndividual(type, suid, kwargs={}, copy_ind=None):
    individual = None
    if copy_ind is not None:
        individual = copy.deepcopy(copy_ind)
    else:
        if type == "Generic":   # make dependant in sim type?
            with open("individual.json", "r") as file:
                individual = json.load(file)
        elif type == "Malaria":
            pass
        else:
            print("individual of type" + type + " does not exist")

    individual["suid"] = suid
    individual.update(kwargs.items())

    return individual


def add(path, sub_path, object, fct=lambda ind: True):
    """Add an object to the data structure path that fulfills a certain criteria e.g. age"""
    for p in [n for n in path if fct(n)]:
        p[sub_path].append(copy.deepcopy(object))


def getAvailableDistributions():
    distributions = [
        {'label': 'gaussian_1000_10', 'value': 'randomGauss'},
        {'label': 'constant_1500', 'value': 'constantDistribution'},
        {'label': 'poisson', 'value': 'PoissonDistribution'}
    ]
    return distributions


def randomGauss():
    return random.gauss(1000, 10)


def PoissonDistribution():
    return int(scipy.stats.poisson.rvs(mu=100,loc=100, size=1)[0])


def myRandom2():
    return random.randint(0, 3)


def constantDistribution():
    return 1500


def setFile(file):
    global dtk
    dtk = dtk_class(file)

def show(handle):
    print(json.dumps(handle, indent=4))


def find(name, handle, currentlevel="dtk.nodes"):
    global counter
    if type(handle) is str and difflib.get_close_matches(name, [handle],cutoff=0.6):
        print (counter, "  Found in: ", currentlevel)
        counter +=1
        return

    if type(handle) is str or not isinstance(handle, collections.Iterable):
        return

    for idx, key in enumerate(handle): # key can be a string or on dict/list/..
        level = currentlevel + "." + key if type(key) is str else currentlevel + "[" + str(idx) + "]"
        try:
            tmp = handle[key]
            if isinstance(tmp, collections.Iterable):
                find(name, key, level + "[]")
            else:
                find(name, key, level)
        except:
            find(name, key, level)    # list or keys of a dict, works in all cases but misses objects in dicts
        if isinstance(handle,dict):
            find(name, handle[key], level)    # check if string is key for a dict


def printParameters(handle, currentlevel="dtk.nodes"):
    global counter
    param = set()

    if type(handle) is str:
        param.add(currentlevel)
        return param

    if not isinstance(handle, collections.Iterable):
        return param

    for idx, d in enumerate(handle):
        level = currentlevel + " " + d if type(d) is str else currentlevel
        param.update(printParameters(d, level))
        if isinstance(handle, dict):
            param.update(printParameters(handle[d], level))

    return param


if __name__ == "__main__":
#    path = "C:/Users/tfischle/Github/DtkTrunk_master/Regression/Generic/71_Generic_RngPerCore_FromSerializedPop"
    path = pathlib.PureWindowsPath(r"C:\Users\tfischle\Github\DtkTrunk_master\Regression\Generic\13_Generic_Individual_Properties")
    serialized_file = "state-00015.dtk"

    # opens and saves all nodes, suid
    pop = dtk_class(str(path) + '/' + serialized_file)


    print(find("age", pop.nodes))
    show(pop.nodes[0].individualHumans[10].m_age)

#    print(find("infection", pop.nodes))






