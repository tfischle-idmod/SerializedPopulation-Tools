import sys, os
sys.path.append("C:\\Users\\tfischle\\GitHub\\DtkTrunk\\Regression\\shared_embedded_py_scripts")
import dtk_FileTools as dft
import dtk_FileSupport as support
import numpy
import random
import matplotlib.pyplot as plt


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
    For each entry in the property list a individual is added.
    '''
    node = handle.nodes[0]
    temp_list = []
    for individual_props in properties:
        copy_ind = support.SerialObject(handle.nodes[node_id].individualHumans[0])
        suid = getNextSuid(handle)
        print ("suid: ", suid)
        copy_ind.suid['id']=suid
        for prop in individual_props:
            copy_ind[prop] = individual_props[prop]
        temp_list.append(copy_ind)
    node.individualHumans.extend(temp_list)
    handle.nodes[0] = node
    write(handle)


def addIndividuals_fixedProp(nodes, number, properties, handle):
    '''
    :param nodes: Node
    :param number: number of indiviudals
    :param properties: properties of the individuals
    :param handle: serialized dtk file

    Adds a number of individuals with the same properties to a list of nodes.
    '''
    for n in nodes:
        for i in range(0,number):
            copy_ind = support.SerialObject(handle.nodes[n].individualHumans[0])
            suid = getNextSuid(handle)
            print("suid: ", suid)
            copy_ind.suid['id'] = suid
            for prop in properties:
                copy_ind[prop] = properties[prop]
            node = handle.nodes[0]
            node.individualHumans.append(copy_ind)
            handle.nodes[0] = node
    write(handle)

def changeSusceptibility(node_ids, number, properties, handle):
    for n in node_ids:
        node = handle.nodes[n]
        for num in range(0,number):
            for prop in properties:
                node.individualHumans[num].susceptibility[prop] = properties[prop]
            handle.nodes[n] = node
    write(handle)


def removeIndividuals(nodes, number, handle):
    for n in nodes:
        node = handle.nodes[n]
        del node.individualHumans[0:number]
        handle.nodes[n] = node
    write(handle)


def setIndividualProperty(individual_idx, prop_value, handle):
    node = handle.nodes[0]
    for idx in individual_idx:
        for prop in prop_value:
            node.individualHumans[idx][prop] = prop_value[prop]
    handle.nodes[0] = node
    write(handle)


def generatePopulation(prop_value, handle):
    addIndividual(0,prop_value, handle)

def write(handle):
    handle.compression = dft.NONE
    dft.write(handle,"my_dtk_file.dtk")

def generatePopulationPyramid():
    bins = [0, 10, 20, 30, 40, 50, 60, 70]
    age_distr = []
    number_of_people_in_bin = 100
    for idx, bin in enumerate(bins[1:],1):
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
    axes[1].hist(x2, bins, color='red')
    axes[0].invert_xaxis()
    plt.show()

    return age_distr

if __name__ == "__main__":
     path = "C:/Users/tfischle/GitHub/DtkTrunk/Regression/Serialization/1300_comparison_with_report_data/output/"
     serialized_file = "state-00023.dtk"
     dtk = dft.read(path + '/' + serialized_file)

     #setIndividualProperty([1,2,3], {"m_is_infected":True}, dtk)
     #addIndividuals_fixedProp([0], 15, {"m_is_infected":True}, dtk)
     #removeIndividuals([0], 3, dtk)

     #changeSusceptibility([0], 1, {"age":1234}, dtk)

     # age_distr = [{"m_age":1, "m_gender": 0, "m_is_infected":True},
     #              {"m_age": 10, "m_gender": 1, "m_is_infected":True},
     #              {"m_age": 47, "m_gender": 0, "m_is_infected":True}]

     age_distr = generatePopulationPyramid()
     generatePopulation(age_distr, dtk)
     write(dtk)