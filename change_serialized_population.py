import sys
sys.path.append("C:\\Users\\tfischle\\Github\\DtkTrunk_master\\Scripts\\serialization")
import dtkFileTools as dft
import dtkFileSupport as support
import random
import matplotlib.pyplot as plt
import collections
import utils
import json
import scipy.stats
import collections



counter =0


def getNextInfectionSuid(handle):
    sim = handle.simulation
    suid = sim["infectionSuidGenerator"]['next_suid']
    sim["infectionSuidGenerator"]['next_suid']['id'] = suid['id'] + sim["infectionSuidGenerator"]['numtasks']
    handle.simulation = sim
    return suid


def getNextIndividualSuid(node_id, handle):
    node = handle.nodes[node_id]
    suid = node["m_IndividualHumanSuidGenerator"]['next_suid']
    node["m_IndividualHumanSuidGenerator"]['id'] = suid['id'] + node["m_IndividualHumanSuidGenerator"]['numtasks']
    handle.nodes[node_id] = node
    return suid['id']


def addIndividual(node_id, properties, handle):
    '''
    :param node_id: the node individual is added to
    :param properties: properties of the individual
    :param handle: serialized dtk file
    :return:

    Adds individuals to a node. The properties of each individual must be given as a list of dictionaries.
    For each entry in the property list an individual is added.
    '''
    node = handle.nodes[node_id]
    for individual_props in properties:
        copy_ind = support.SerialObject(handle.nodes[0].individualHumans[0])
        suid = getNextIndividualSuid(node_id, handle)
        print("suid: ", suid)
        copy_ind.suid['id']=suid
        for prop in individual_props:
            copy_ind[prop] = individual_props[prop]
        node.individualHumans.append(copy_ind)
    handle.nodes[node_id] = node


def addIndividuals_sameProperties(node_id, number, properties, handle):
    '''
    :param nodes: Node
    :param number: number of indiviudals
    :param properties: properties of the individuals
    :param handle: serialized dtk file

    Adds a number of individuals with the same properties to a list of nodes.
    '''
    node = handle.nodes[node_id]
    for i in range(0, number):
        copy_ind = support.SerialObject(handle.nodes[0].individualHumans[0])
        suid = getNextIndividualSuid(node_id, handle)
        print("suid: ", suid)
        copy_ind.suid['id'] = suid
        for prop in properties:
            copy_ind[prop] = properties[prop]
        node.individualHumans.append(copy_ind)
        handle.nodes[node_id] = node


def changeSusceptibility(node_id, number_of_ind, properties, handle):
    node = handle.nodes[node_id]
    for num in range(0,number_of_ind):
        for prop in properties:
            node.individualHumans[num].susceptibility[prop] = properties[prop]
        handle.nodes[node_id] = node


def removeIndividuals(node_id, number_of_ind, handle):
    node = handle.nodes[node_id]
    del node.individualHumans[0:number_of_ind]
    handle.nodes[node_id] = node


def setIndividualPropertyInfections(node_id, individual_idx, prop_value, handle):
    node = handle.nodes[node_id]
    for idx in individual_idx:
        for prop in prop_value:
            node['individualHumans'][idx]['infections'][0][prop] = prop_value[prop]
    handle.nodes[node_id] = node


def generatePopulation(prop_value, handle):
    addIndividual(0,prop_value, handle)


def write(handle):
    handle.compression = dft.NONE
    dft.write(handle,"my_dtk_file.dtk")


def find(name, handle, currentlevel="dtk.nodes"):
    global counter
    if type(handle) is str and name in handle:
        print (counter, "  Found in: ", currentlevel)
        counter +=1
        return

    if type(handle) is str or not isinstance(handle, collections.Iterable):
        return

    for idx, d in enumerate(handle):
        level = currentlevel + " " + d if type(d) is str else currentlevel + "[" + str(idx) + "]"
        find(name, d, level)    # list or keys of a dict, works in all cases but misses objects in dicts
        if isinstance(handle,dict):
            find(name, handle[d], level)    # check if string is key for a dict


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


def setIndividualProperty(node_id, individual_idx, prop_value, handle):
    """change key value of some individual properties, given as a list of indices."""
    node = handle.nodes[node_id]
    for idx in individual_idx:
        for prop in prop_value:
            node['individualHumans'][idx][prop] = prop_value[prop]
    handle.nodes[node_id] = node


def setPropertyValues_Individual(node_id, param_value, handle):
    """ length of param_value must be equal to number of individuals.
     Every entry in paramvalue is a dict wit one or several key-value pairs."""
    node = handle.nodes[node_id]
    for param, ind in zip(param_value, node['individualHumans']):
        ind.update(param)
    handle.nodes[node_id] = node


def getPropertyValues_Individual(node_id, handle, property):
    """returns list values for property property"""
    node = handle.nodes[node_id]
    return [ len(ind[property]) if isinstance(ind[property], collections.Iterable) else ind[property] for ind in node.individualHumans ]


def getIndividualsWithProperty(node_id, handle, fct=lambda ind: True):
    """ get all individuals with a certain condition. condition is given by fct."""
    individuals = handle.nodes[node_id].individualHumans
    return [ind for ind in individuals if fct(ind)]


def getListIndividualProperties(node_id, handle):
    node = handle.nodes[node_id]
    return [prop for prop in node.individualHumans[0]]


def createInfection(type, suid, kwargs={}):
    infection = None
    if type == "Generic":
        with open("infection.json", "r") as file:
            infection = json.load(file)
    elif type == "Malaria":
        pass
    else:
        print("Infection of type" + type + " does not exist")

    infection["suid"] = suid
    infection.update(kwargs.items())

    return infection


def addInfectionToIndividuals(node_id, handle, infection, fct=lambda ind: True):
    node = handle.nodes[node_id]
    for individual in [n for n in node.individualHumans if fct(n)]:
        print(individual)
        infection["suid"] = getNextInfectionSuid(dtk)
        individual.infections.append(infection)
        print(individual)
    handle.nodes[node_id] = node


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


path = "C:/Users/tfischle/Github/DtkTrunk_master/Regression/Generic/71_Generic_RngPerCore_FromSerializedPop"
serialized_file = "state-00015.dtk"
dtk = dft.read(path + '/' + serialized_file)


if __name__ == "__main__":
#    path = "C:/Users/tfischle/Github/DtkTrunk_master/Regression/Generic/71_Generic_RngPerCore_FromSerializedPop"
#    serialized_file = "state-00015.dtk"
 #   dtk = dft.read(path + '/' + serialized_file)

    properties = getPropertyValues_Individual(0, dtk, "infections")
    print(properties)
#    plt.plot(properties, "+")
#    plt.show()

    #     print (listProperties(0, dtk))

    # print(find("infection", dtk.nodes[0]))




    # print(getPropertyValues_Individual(0, dtk, "m_age"))
    #
    #
    # infected_ind = getIndividualsWithProperty(0, dtk, lambda ind: ind.infections)
    #
    # infection_init = {"duration": 123, "incubation_timer": 456}
    #
    # new_infection1 = createInfection("Generic", getNextInfectionSuid(dtk), infection_init)
    # print(new_infection1)
    #
    # new_infection2 = createInfection("Generic", getNextInfectionSuid(dtk), infection_init)
    # print(new_infection2)
    #
    # addInfectionToIndividuals(0, dtk, new_infection1, lambda ind: ind["m_age"] > 43500)



    # for ind in infected_ind:
    #     print("Individual: " + str(ind["suid"]))
    #     print(ind.infections)
    #     print()
    #
    # for infection in infected_ind[0].infections:
    #     print(infection)
    #
    # infection = infected_ind[0].infections[0]
    #
    # with open("infection.json", "w") as file:
    #     json.dump(infection, file)

#   print(printParameters(dtk.nodes))

#    temp = createDistribution("m_age", len(dtk.nodes[0].individualHumans), randomGauss)
    temp = utils.createDistribution("m_gender", len(dtk.nodes[0].individualHumans), myRandom2)
    print(temp)

    setPropertyValues_Individual(0, temp, dtk)

    print(getPropertyValues_Individual(0, dtk, "m_gender"))

#    age = getPropertyValues_Individual(0, dtk, "m_gender")

#    plt.hist(age, bins=30)
#    plt.ylabel('Probability')
#   plt.show()

    #setIndividualProperty(0, [1,3], {"m_is_active":False}, dtk)
    #addIndividuals_sameProperties(0, 15, {"m_is_infected":True}, dtk)
    #write(dtk)

    #removeIndividuals(0, 3, dtk)
    #write(dtk)


    #changeSusceptibility(0, 1, {"age":1234}, dtk)
    #write(dtk)


    # age_distr = [{"m_age":1, "m_gender": 0, "m_is_infected":True},
    #              {"m_age": 10, "m_gender": 1, "m_is_infected":True},
    #              {"m_age": 47, "m_gender": 0, "m_is_infected":True}]

    # age_distr = generatePopulationPyramid()
    # generatePopulation(age_distr, dtk)
    # write(dtk)

    myhandle = dtk.nodes[0]
    myhandle["enable_infectivity_reservoir"] = 1
    #dtk.nodes[0] = myhandle

    # find("enable_infectivity_reservoir", dtk.nodes, "dtk.nodes")
    # find("birth_rate_boxcar_end_time", dtk.nodes, "dtk.nodes")
    # find("infectivity_reservoir_end_time", dtk.nodes, "dtk.nodes")

    # setIndividualPropertyInfections(0, range(0,100), {"duration":100, "m_is_active":False, "incubation_timer":123}, dtk)
    # write(dtk)

    # for idx_human, h in enumerate(dtk.nodes[0].individualHumans):
    #  for inf in h.infections:
    #       print ("hum: ", idx_human, "   dur: ", inf.duration, "   active: ", inf.m_is_active, "   inc_t: ", inf.incubation_timer)
