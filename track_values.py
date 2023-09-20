import sys

sys.path.append("C:\\Users\\tfischle\\Github\\DtkTrunk_master\\Scripts\\serialization")
import emod_api.serialization.SerializedPopulation as sp
import pathlib
import numpy
import glob
import multiprocessing

counter = 0
nextInfectionSuid_initialized = False
nextInfectionSuid_suid = None
dtk = None

def get_avg(file_path):
    ser_pop = sp.SerializedPopulation(file_path)

    node_0 = ser_pop.nodes[0]

    # print(sp.find("m_cytokines", node_0))
    list_m_cytokines = []
    for i in node_0.individualHumans:
        list_m_cytokines.append(i.susceptibility.m_cytokines)

    arr_m_cytokines = numpy.array(list_m_cytokines)
    avg_m_cytokines = sum(arr_m_cytokines) / arr_m_cytokines.size
    return (avg_m_cytokines, file_path)


if __name__ == "__main__":
    serialized_file = "state-00200.dtk"
    path = pathlib.PureWindowsPath(r"C:\Users\tfischle\Github\DtkTrunk\Regression\Serialization\Josh_PfHRP2_from_burnin\testing")
    sp_files = glob.glob(str(pathlib.PureWindowsPath(path, "*.dtk")))
    print("files: ", sp_files)

    avg_m_cytokines = []
    pool_obj = multiprocessing.Pool()
#    print(pool_obj)
    res = pool_obj.map(get_avg, sp_files)

#    for file_path in sp_files:
        # ser_pop = sp.SerializedPopulation(file_path)
        #
        # node_0 = ser_pop.nodes[0]
        #
        # # print(sp.find("m_cytokines", node_0))
        # list_m_cytokines = []
        # for i in node_0.individualHumans:
        #     list_m_cytokines.append(i.susceptibility.m_cytokines)
        #
        # arr_m_cytokines = numpy.array(list_m_cytokines)
        # avg_m_cytokines.append(sum(arr_m_cytokines) / arr_m_cytokines.size)

    print(res)


