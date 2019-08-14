import unittest
import change_serialized_population
import pathlib
import dtkFileTools as dft
import dtkFileSupport

path = pathlib.PureWindowsPath( r"C:\Users\tfischle\Github\DtkTrunk_master\Regression\Generic\13_Generic_Individual_Properties")
serialized_file = "state-00015.dtk"

class AddInfectionTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_add_infection(self):
        dtk_obj = change_serialized_population.SerializedPopulation(str(path) + '/' + serialized_file)

        # count existing infections
        number_of_infections = sum( [len(dtk_obj.nodes[0].individualHumans[r].infections) for r in range(3, 10)])

        # create infection and add to individuals
        infection_init = {"duration": 123, "incubation_timer": 456}
       # new_infection1 = change_serialized_population.createInfection( dtk_obj.getNextInfectionSuid(), kwargs=infection_init, from_file="infection.json")

        filter_fct = lambda ind: ind.suid.id in range(3,10) # 7, starting from suid.id:3
        dtk_obj.addInfection(dtk_obj.nodes[0], "infection.json", filter_fct)

        new_number_of_infections = sum( [len(dtk_obj.nodes[0].individualHumans[r].infections) for r in range(1,7)])

        success = number_of_infections + 7 == new_number_of_infections
        self.assertTrue(success, "Error")


    def test_add(self):
        Expected_Number_Added_Infections = 5

        # create infection and add to individuals
        infection_init = {"duration": 123, "incubation_timer": 456}
        new_infection = change_serialized_population.createInfection({'suid': {'id': 123}}, from_file="infection.json", kwargs=infection_init)
        list_temp = [dtkFileSupport.SerialObject({"test_list": []}), dtkFileSupport.SerialObject({"test_list": []}) ]
        change_serialized_population.add(list_temp, "test_list", new_infection)


        a = list_temp[0]["test_list"]
        b = list_temp[1]["test_list"]

        success_ref = list_temp[0]["test_list"] is not list_temp[1]["test_list"]
        list_temp[0]["test_list"][0]["duration"] = 999999
        success_value = not list_temp[0]["test_list"][0]["duration"] == list_temp[1]["test_list"][0]["duration"]
        self.assertTrue(success_ref and success_value, "Error")


    def test_add2(self):
        Expected_Number_Added_Infections = 5
        dtk_obj = change_serialized_population.SerializedPopulation(str(path) + '/' + serialized_file)

        # count existing infections
        number_of_infections = sum([len(dtk_obj.nodes[0].individualHumans[r].infections) for r in range(0, 10)])

        # create infection and add to individuals
        infection_init = {"duration": 123, "incubation_timer": 456}
        new_infection = change_serialized_population.createInfection(dtk_obj.getNextInfectionSuid(),
                                                                      kwargs=infection_init, from_file="infection.json")

        individual_path = dtk_obj.nodes[0].individualHumans
        filter_fct = lambda ind: ind["m_age"] < 12000 and ind.suid.id in range(3,10)
        change_serialized_population.add(individual_path, "infections", new_infection, filter_fct)

        new_total_number_of_infections = sum([len(dtk_obj.nodes[0].individualHumans[r].infections) for r in range(0, 10)])
        number_added_infections = new_total_number_of_infections - number_of_infections

        success = number_added_infections == Expected_Number_Added_Infections
        self.assertTrue(success, "Error, expected number of new infections: " + str(Expected_Number_Added_Infections) + " actual number of added infections: " + str(number_added_infections))


    def test_get_setPropertyValues_Individual(self):
        dtk_obj = change_serialized_population.SerializedPopulation(str(path) + '/' + serialized_file)

        new_properties = [{"m_age": 7}] * 1000  # one dict for each individual

        change_serialized_population.setPropertyValues_Individual(0, new_properties, dtk_obj)
        properties = change_serialized_population.getPropertyValues_Individual(0, dtk_obj, "m_age")

        success = sum(properties) == 1000*7
        self.assertTrue(success, "Error")


    def test_createIndividual(self):
        New_Age = 3
        dtk_obj = change_serialized_population.SerializedPopulation(str(path) + '/' + serialized_file)
        number_individuals = len(dtk_obj.nodes[0].individualHumans)

        copy_ind = dtk_obj.nodes[0].individualHumans[0]
        kwargs = {"m_age": New_Age}
        ind = change_serialized_population.createIndividual(dtk_obj.getNextIndividualSuid(0), copy_ind = copy_ind, kwargs=kwargs )
        print(ind)
        dtk_obj.nodes[0].individualHumans.append(ind)

        new_number_individuals = len(dtk_obj.nodes[0].individualHumans)
        success_copy_ind = not copy_ind.m_age == New_Age
        success_added = number_individuals + 1 == new_number_individuals
        success_kwargs = dtk_obj.nodes[0].individualHumans[new_number_individuals-1]["m_age"] == New_Age
        self.assertTrue(success_added and success_kwargs and success_copy_ind, "Error")


if __name__ == "__main__":
    unittest.main()