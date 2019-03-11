import unittest
import change_serialized_population
import pathlib

path = pathlib.PureWindowsPath( r"C:\Users\tfischle\Github\DtkTrunk_master\Regression\Generic\13_Generic_Individual_Properties")
serialized_file = "state-00015.dtk"

class AddInfectionTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_add_infection(self):
        dtk_obj = change_serialized_population.dtk_class(str(path) + '/' + serialized_file)

        # count existing infections
        number_of_infections = sum( [len(dtk_obj.nodes[0].individualHumans[r].infections) for r in range(3, 10)] )

        # create infection and add to individuals
        infection_init = {"duration": 123, "incubation_timer": 456}
        new_infection1 = change_serialized_population.createInfection("Generic", dtk_obj.getNextInfectionSuid(), infection_init)

        filter_fct = lambda ind: ind.suid.id in range(3,10) # 7, starting from suid.id:3
        change_serialized_population.addInfectionToIndividuals_fct(dtk_obj.nodes[0], new_infection1, filter_fct)

        new_number_of_infections = sum( [len(dtk_obj.nodes[0].individualHumans[r].infections) for r in range(2,9)])

        success = number_of_infections + 7 == new_number_of_infections
        self.assertTrue(success, "Error")


    def test_add(self):
        dtk_obj = change_serialized_population.dtk_class(str(path) + '/' + serialized_file)

        # count existing infections
        number_of_infections = sum([len(dtk_obj.nodes[0].individualHumans[r].infections) for r in range(3, 10)])

        # create infection and add to individuals
        infection_init = {"duration": 123, "incubation_timer": 456}
        new_infection1 = change_serialized_population.createInfection("Generic", dtk_obj.getNextInfectionSuid(),
                                                                      infection_init)

        obj_path = dtk_obj.nodes[0].individualHumans
        filter_fct = lambda ind: ind["m_age"] > 43500
        change_serialized_population.add(obj_path, new_infection1, filter_fct)

        new_number_of_infections = sum([len(dtk_obj.nodes[0].individualHumans[r].infections) for r in range(3, 10)])

        success = number_of_infections + 7 == new_number_of_infections
        self.assertTrue(success, "Error")


    def test_get_setPropertyValues_Individual(self):
        dtk_obj = change_serialized_population.dtk_class(str(path) + '/' + serialized_file)

        new_properties = [{"m_age": 7}] * 1000  # one dict for each individual

        change_serialized_population.setPropertyValues_Individual(0, new_properties, dtk_obj)
        properties = change_serialized_population.getPropertyValues_Individual(0, dtk_obj, "m_age")

        success = sum(properties) == 1000*7
        self.assertTrue(success, "Error")


    def test_createIndividual(self):
        dtk_obj = change_serialized_population.dtk_class(str(path) + '/' + serialized_file)
        number_individuals = len(dtk_obj.nodes[0].individualHumans)

        copy_ind = dtk_obj.nodes[0].individualHumans[0]
        kwargs = {"m_age": 3}
        ind = change_serialized_population.createIndividual("Generic", dtk_obj.getNextIndividualSuid(0), copy_ind = copy_ind, kwargs=kwargs )
        print(ind)
        dtk_obj.nodes[0].individualHumans.append(ind)

        new_number_individuals = len(dtk_obj.nodes[0].individualHumans)
        success_added = number_individuals + 1 == new_number_individuals
        success_kwargs = dtk_obj.nodes[0].individualHumans[new_number_individuals-1].m_age == 3
        self.assertTrue(success_added and success_kwargs, "Error")


if __name__ == "__main__":
    unittest.main()