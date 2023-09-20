import sys

sys.path.append("C:\\Users\\tfischle\\Github\\DtkTrunk_master\\Scripts\\serialization")
import emod_api.serialization.dtkFileTools as dft
import random
import json
import scipy.stats
import collections
import pathlib
import difflib
import copy

counter = 0
nextInfectionSuid_initialized = False
nextInfectionSuid_suid = None
dtk = None


class SerializedPopulation:

    def __init__(self, file):
        self.nextInfectionSuid_suid = None
        self.nextInfectionSuid_initialized = False
        self.dtk = dft.read(file)
        self._nodes = [n for n in self.dtk.nodes]

    def get_nodes(self):
        return self._nodes

    nodes = property(get_nodes)

    def close(self):
        """ Has to be called to save all the changes made to the node(s)."""
        for idx in range(len(self._nodes)):
            self.dtk.nodes[idx] = self._nodes[idx]

    def write(self, output_file="my_sp_file.dtk"):
        self.close()
        sim = self.dtk.simulation
        sim["infectionSuidGenerator"]['next_suid'] = self.getNextInfectionSuid()
        self.dtk.simulation = sim

        self.dtk.compression = dft.LZ4      #dft.NONE gives an error and dtkFileTools __write_chunks__
#        self.dtk.compressed = False
        dft.write(self.dtk, output_file)

    def getNextInfectionSuid(self):
        sim = self.dtk.simulation
        if not self.nextInfectionSuid_initialized:
            self.nextInfectionSuid_suid = sim["infectionSuidGenerator"]['next_suid']
            self.nextInfectionSuid_initialized = True
        else:
            self.nextInfectionSuid_suid['id'] = self.nextInfectionSuid_suid['id'] + sim["infectionSuidGenerator"]['numtasks']

        return dict(self.nextInfectionSuid_suid)

    def getNextIndividualSuid(self, node_id):
        suid = self._nodes[node_id]["m_IndividualHumanSuidGenerator"]['next_suid']
        self._nodes[node_id]["m_IndividualHumanSuidGenerator"]['id'] = suid['id'] + self._nodes[node_id]["m_IndividualHumanSuidGenerator"]['numtasks']
        return dict(suid)

    def addInfection(self, node, infection, filter_fct=lambda x: True):
        for idx in range(0, len(node["individualHumans"])):
            if filter_fct(node["individualHumans"][idx]):
                temp_infection = dict(infection)
                temp_infection["suid"] = self.getNextInfectionSuid()
                node["individualHumans"][idx]['infections'].append(temp_infection)
                node["individualHumans"][idx].m_is_infected = True



def loadInfection(from_file=None):
    """returns a dictionary"""
    if from_file is not None:
        try:
            with open(from_file, "r") as file:
                infection = json.load(file)
        except Exception as ex:
            print("Could not create infection from file: ", from_file)
            print(str(ex))
    return infection


def removeNumberIndividuals(node_id, number_of_ind, handle):
    node = handle.nodes[node_id]
    del node.individualHumans[0:number_of_ind]


def removeIndividuals(node_id, handle, remove_fct):
    node = handle.nodes[node_id]
    node.individualHumans = [ind for ind in node.individualHumans if not remove_fct(ind)]


def changeSusceptibility(node_id, number_of_ind, properties, handle):
    node = handle.nodes[node_id]
    for num in range(0, number_of_ind):
        for prop in properties:
            node.individualHumans[num].susceptibility[prop] = properties[prop]


def setIndividualPropertyInfections(node_id, individual_idx, prop_value, handle):
    node = handle.nodes[node_id]
    for idx in individual_idx:
        for prop in prop_value:
            node['individualHumans'][idx]['infections'][0][prop] = prop_value[prop]


def generatePopulation(prop_values, node, copy_ind):
    # copy_ind = dtk_obj.nodes[0].individualHumans[0]
    for individual_props in prop_values:
        ind = createIndividual("Generic", node.getNextIndividualSuid(0), copy_ind=copy_ind, from_file="individual.json",
                               kwargs=individual_props)
        node.individualHumans.append(ind)


def setAttributes(param_value, handle):
    """ length of param_value must be equal to number of individuals.
     Every entry in paramvalue is a dict wit one or several key-value pairs."""
    for param, ind in zip(param_value, handle):
        ind.update(param)


def setAttribute(attribute, handle, filter_fct=lambda x: True):
    """ one attribute (dict with one or several key/value pairs)
     Change attribute(s) of individusl who math a certain condition"""
    for p in [n for n in handle if filter_fct(n)]:
        p.update(attribute)


def getAttributeValues(handle, property, filter_fct=lambda x: True):
    """returns list values for property property or if the property is a list, the length of the list"""
    select_fct = lambda x: x[property]
    return getPropertyValues2(handle, select_fct=select_fct, filter_fct=filter_fct)


def getPropertyValues2(handle, select_fct=lambda x: x, filter_fct=lambda x: True):
    """returns list of values. filter_fct is to filter on one or several attributes, the select_fct can be used to
    further process the data. E.g. filter on the age of an individual then count all infections."""
    return [select_fct(ind) for ind in handle if filter_fct(ind)]


def getIndividualsWithProperty(handle, fct=lambda ind: True):
    """ get all individuals that fulfill a certain condition. Condition is given by fct."""
    individuals = handle.individualHumans
    return [ind for ind in individuals if fct(ind)]


def addInfectionToIndividuals_fct(handle, infection, fct=lambda ind: True):
    """Add infection to individuals that fulfill a certain criteria e.g. age"""
    add(handle["individualHumans"], "infections", infection, fct)


def createIndividual(suid, kwargs={}, copy_ind=None, from_file=None):
    individual = None
    if copy_ind is not None:
        individual = copy.deepcopy(copy_ind)
    elif from_file is not None:
        try:
            with open(from_file, "r") as file:
                individual = json.load(file)
        except:
            print("Could not create individual from file: ", from_file)
    else:
        print("Please provide at least one template.")

    individual["suid"] = suid
    individual.update(kwargs.items())

    return individual


def add(path, sub_path, object, fct=lambda ind: True):
    """Add an object to the data structure path that fulfills a certain criteria e.g. age"""
    for p in [n for n in path if fct(n)]:
        p[sub_path].append(copy.deepcopy(object))


def add2(path, sub_path, object):
    path[sub_path].insert(0, copy.deepcopy(object))


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
    return int(scipy.stats.poisson.rvs(mu=100, loc=100, size=1)[0])


def myRandom2():
    return random.randint(0, 3)


def constantDistribution():
    return 1500


def setFile(file):
    global dtk
    dtk = SerializedPopulation(file)


def show(handle):
    print(json.dumps(handle, indent=4))


def find(name, handle, currentlevel="dtk.nodes"):
    global counter
    if type(handle) is str and difflib.get_close_matches(name, [handle], cutoff=0.6):
        print(counter, "  Found in: ", currentlevel)
        counter += 1
        return

    if type(handle) is str or not isinstance(handle, collections.Iterable):
        return

    for idx, key in enumerate(handle):  # key can be a string or on dict/list/..
        level = currentlevel + "." + key if type(key) is str else currentlevel + "[" + str(idx) + "]"
        try:
            tmp = handle[key]
            if isinstance(tmp, collections.Iterable):
                find(name, key, level + "[]")
            else:
                find(name, key, level)
        except:
            find(name, key, level)  # list or keys of a dict, works in all cases but misses objects in dicts
        if isinstance(handle, dict):
            find(name, handle[key], level)  # check if string is key for a dict


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


# ----------------------------------------------------------------------------------------------
# Deprecated Functions
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







if __name__ == "__main__":
    serialized_file = "state-00010.dtk"
    path = pathlib.PureWindowsPath(r"C:\Users\tfischle\Desktop\Eradication_2.21\output", serialized_file)

    ser_pop = SerializedPopulation(path)

    node_0 = ser_pop.nodes[0]

    pass    # breakpoint






    #  path_from = pathlib.PureWindowsPath(r"C:\Users\tfischle\Github\DtkTrunk_master\Regression\Generic\72_Generic_RngPerNode_FromSerializedPop")
    # path_save = pathlib.PureWindowsPath(
    #     r"C:\Users\tfischle\Github\DtkTrunk_master\Regression\Generic\13_Generic_Individual_Properties\state-00015_test.dtk")
    #
    # ser_pop = SerializedPopulation(str(path) + '/' + serialized_file)
    # ser_pop_from = SerializedPopulation(str(path_from) + '/' + serialized_file)
    #
    #
    # individual = createIndividual(ser_pop.getNextIndividualSuid(0), copy_ind=ser_pop.nodes[0].individualHumans[0])
    # print(individual)
    # add2(ser_pop.nodes[0],"individualHumans", individual)
    #
    # ser_pop.close()
    # ser_pop.write(path_save)


    # df = pandas.DataFrame.from_records([ser_pop.nodes[0]], columns=ser_pop.nodes[0].keys())
    #    df = pandas.io.json.json_normalize(ser_pop.nodes[0].individualHumans, 'infections')
    # df1 = pandas.DataFrame(ser_pop.nodes[0].individualHumans)
#    df = pandas.io.json.json_normalize(ser_pop.nodes[0].individualHumans, 'infections', ['infectiousness'])
    #    df = pandas.io.json.json_normalize(ser_pop.nodes[0].individualHumans)

    # int = [pandas.DataFrame(i) for i in df["interventions"]]

    #    print(int)

    # import tabulate
    # print(tabulate.tabulate(interventions[3], headers='keys', tablefmt='psql'))
    #
    # print(interventions[0]["__class__"])

#    df.to_html("table.html")

    # fct = lambda ind: len(ind["infections"]) >= 1
    # ind_values = getPropertyValues(ser_pop.nodes[0].individualHumans, "m_age", sub_path="infections", fct=fct)
    #
    # print(find("age", ser_pop.nodes))
    # show(ser_pop.nodes[0].individualHumans[10].m_age)
    #
    # node0 = ser_pop.nodes[0]
    # ind_values = getPropertyValues(node0.individualHumans, "m_age")
    #
    # plt.hist(ind_values, bins=20)
    # plt.title("m_age")
    # plt.xlabel("days")
    # plt.ylabel("number of indivuals")
    # plt.show()

#    print(find("infection", pop.nodes))
