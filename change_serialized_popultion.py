import sys, os
sys.path.append("C:\\Users\\tfischle\\Github\\DtkTrunk_master\\Scripts\\serialization")
import dtkFileTools as dft
import dtkFileSupport as support
import random
import matplotlib.pyplot as plt
import collections



counter =0

def getNextSuid(handle):
    sim = handle.simulation
    suid = sim.individualHumanSuidGenerator['next_suid']
    sim.individualHumanSuidGenerator['next_suid']['id'] = suid['id'] + sim.individualHumanSuidGenerator['numtasks']
    handle.simulation = sim
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
        suid = getNextSuid(handle)
        print ("suid: ", suid)
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
        suid = getNextSuid(handle)
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


def createDistribution(parameter, number, fct=1):
    distribution = []
    for i in range(number):
        distribution.append({parameter: fct()})
    return distribution


def generatePopulationPyramid():
    bins = [0, 10, 20, 30, 40, 50, 60, 70]
    age_distr = []
    number_of_people_in_bin = 400
    for idx, bin in enumerate(bins[1:], 1):
        for num in range(0,number_of_people_in_bin):
            m_age = random.randint(bins[idx-1],bins[idx]-1)             # bins[idx-1] <= x < bins[idx]
            m_gender = random.randint(0,1)
            age_distr.append({'m_age': m_age, "m_gender":m_gender})
        mortality = random.normalvariate(0.85, 0.1)
        number_of_people_in_bin = (int)(number_of_people_in_bin * mortality)  #decreasing with age

    x1 = [age['m_age'] for age in age_distr if age['m_gender']==0]
    x2 = [age['m_age'] for age in age_distr if age['m_gender'] == 1]

    fig, axes = plt.subplots(ncols=2, sharey=True)
    axes[0].hist(x1, bins)
    axes[0].set(xlabel="Age-Group", ylabel="Population", title = "gender==0")
    axes[1].hist(x2, bins, color='red')
    axes[1].set(xlabel="Age-Group", title = "gender==1")
    axes[0].invert_xaxis()
    plt.show()

    return age_distr


def find(name, handle, currentlevel="dtk.nodes"):
    global counter
    if type(handle) is str and name in handle:
        print (counter, "  Found in: ", currentlevel)
        counter +=1
        return

    if type(handle) is str or not isinstance(handle, collections.Iterable):
        return

    for idx, d in enumerate(handle):
        level = currentlevel + " " + d if type(d) is str else currentlevel + str(idx)
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
    node = handle.nodes[node_id]
    for idx in individual_idx:
        for prop in prop_value:
            node['individualHumans'][idx][prop] = prop_value[prop]
    handle.nodes[node_id] = node


def setPropertyValues_Individual(node_id, param_value, handle):
    node = handle.nodes[node_id]
    for param, ind in zip(param_value, node['individualHumans']):
        for p in param:
            ind[p] = param[p]
    handle.nodes[node_id] = node


def getPropertyValues_Individual(node_id, handle, property):
    node = handle.nodes[node_id]
    return [ind[property] for ind in node.individualHumans]


def listProperties(node_id, handle):
    node = handle.nodes[node_id]
    b = set()
    for ind in node.individualHumans:
        for i in ind:
            b.add(i)
    return b

def myRandom():
    return random.gauss(0, 1)

def myRandom2():
    return random.randint(0, 3)


if __name__ == "__main__":
    path = "C:/Users/tfischle/Github/DtkTrunk_master/Regression/Generic/71_Generic_RngPerCore_FromSerializedPop"
    serialized_file = "state-00015.dtk"
    dtk = dft.read(path + '/' + serialized_file)

    properties = getPropertyValues_Individual(0, dtk, "m_gender")
#    plt.plot(properties, "+")
#    plt.show()

    #     print (listProperties(0, dtk))

#    print(find("gender", dtk.nodes[0]))

#   print(printParameters(dtk.nodes))

#    temp = createDistribution("m_age", len(dtk.nodes[0].individualHumans), random.gauss)

    temp = createDistribution("m_gender", len(dtk.nodes[0].individualHumans), myRandom2)

    print(temp)

    setPropertyValues_Individual(0, temp, dtk)

    age = getPropertyValues_Individual(0, dtk, "m_gender")

    plt.hist(age, bins=30)
    plt.ylabel('Probability')

    plt.show()

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
