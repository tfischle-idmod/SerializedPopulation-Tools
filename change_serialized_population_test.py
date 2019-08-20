import unittest
import change_serialized_population
import pathlib
import dtkFileSupport
import dtk_utils.regression
import os
import subprocess

serialized_file = "state-00015.dtk"
output_dir = "output"
path_dtk_file = os.path.join(r"Dtk_tests\0_setUp\output", serialized_file)

path_eradication = os.path.normpath(r"C:\Users\tfischle\Github\DtkTrunk_master\Eradication\x64\Release\eradication.exe")
path_setUp_dir = os.path.normpath(r".\Dtk_tests\0_setUp")


class AddInfectionTest(unittest.TestCase):
    def setUp(self):
        """ called before evey test"""
        pass

    @classmethod
    def setUpClass(cls):
        """ Only called once. Create *.dtk file with current eradication.exe"""
        dtk_utils.regression.flattenConfig(os.path.join(path_setUp_dir, "param_overrides.json"))
        os.chdir(os.path.normpath(path_setUp_dir))
        p = subprocess.call([path_eradication, "-C", "config.json"])
        os.chdir(os.path.normpath("..\.."))

    def test_infection_suid(self):
        """ Add infection to several individuals check suid of added infections."""
        # load and write
        dtk_obj = change_serialized_population.SerializedPopulation(path_dtk_file)

        filter_fct = lambda ind: ind.suid.id in range(0, 10)  # add
        individuals = [ind for ind in dtk_obj.nodes[0].individualHumans if filter_fct(ind)]  # group of individuals
        assert (len(individuals) > 2, "We want at least three individuals to check the suid of new infections.")

        # add infection to every individual
        new_infection = change_serialized_population.loadInfection(from_file="infection.json")
        dtk_obj.addInfection(dtk_obj.nodes[0], new_infection, filter_fct)

        numtasks = dtk_obj.dtk.simulation["infectionSuidGenerator"]['numtasks']
        individuals = [ind for ind in dtk_obj.nodes[0].individualHumans if filter_fct(ind)]

        prev_suid = individuals[0].infections[-1]['suid']['id']

        for i in range(1, len(individuals)):
            current_suid = individuals[i].infections[-1]['suid']['id']
            success = prev_suid + numtasks == current_suid
            self.assertTrue(success, "Error. Suid of infections is not correct.")
            prev_suid = current_suid

        dtk_obj.write(os.path.join(output_dir, "test_infection_suid.dtk"))

        # load saved dtk file and check saved suids
        dtk_obj_changed = change_serialized_population.SerializedPopulation(os.path.join(output_dir, "test_infection_suid.dtk"))

        individuals_changed = [ind for ind in dtk_obj_changed.nodes[0].individualHumans if filter_fct(ind)]

        prev_suid = individuals_changed[0].infections[-1]['suid']['id']

        for i in range(1, len(individuals_changed)):
            current_suid = individuals_changed[i].infections[-1]['suid']['id']
            success = prev_suid + numtasks == current_suid
            self.assertTrue(success, "Error. Suid of infections in loaded dtk file is not correct.")
            prev_suid = current_suid

    def test_removeIndividuals(self):
        """ load *.dtk file, remove all individuals that match a certain condition, write *.dtk file, load again and
        compare expected number to actual number of individuals."""

        dtk_obj = change_serialized_population.SerializedPopulation(path_dtk_file)

        number_individuals_total = len([ind_greater for ind_greater in dtk_obj.nodes[0].individualHumans])

        remove_fct = lambda ind: ind.m_age > 30000
        number_individuals_to_be_removed = len(
            [ind_greater for ind_greater in dtk_obj.nodes[0].individualHumans if ind_greater.m_age > 30000])
        change_serialized_population.removeIndividuals(0, dtk_obj, remove_fct)

        dtk_obj.write(os.path.join(output_dir, "test_removeIndividuals.dtk"))

        dtk_obj_changed = change_serialized_population.SerializedPopulation(
            os.path.join(output_dir, "test_removeIndividuals.dtk"))

        number_individuals_after_removing = len(dtk_obj_changed.nodes[0].individualHumans)
        success = number_individuals_total - number_individuals_to_be_removed == number_individuals_after_removing

        self.assertTrue(success, "Error")

    def test_add_infection(self):
        """adds an infection to several individuals"""
        dtk_obj = change_serialized_population.SerializedPopulation(path_dtk_file)

        # count existing infections
        filter_fct = lambda ind: ind.suid.id in range(3, 10)  # 7, starting from suid.id:3
        number_of_infections = sum(
            [len(ind.infections) for ind in dtk_obj.nodes[0].individualHumans if filter_fct(ind)])  # sum up infections

        # create infection and add to individuals
        infection_init = {"duration": 123, "incubation_timer": 456}
        new_infection = change_serialized_population.loadInfection(from_file="infection.json")
        new_infection.update(infection_init.items())

        dtk_obj.addInfection(dtk_obj.nodes[0], new_infection, filter_fct)

        new_number_of_infections = sum(
            [len(ind.infections) for ind in dtk_obj.nodes[0].individualHumans if filter_fct(ind)])

        success = number_of_infections + 7 == new_number_of_infections
        self.assertTrue(success, "Error.")

    def test_add(self):
        """ Create a list with two SerialObjects. Test if for each list one infection object is created (so not only one
         object that is referenced twice. """

        # create infection and add to individuals
        infection_init = {'suid': {'id': 123}, "duration": 123, "incubation_timer": 456}
        new_infection = change_serialized_population.loadInfection(from_file="infection.json")
        new_infection.update(infection_init.items())

        list_temp = [dtkFileSupport.SerialObject({"test_list": []}), dtkFileSupport.SerialObject({"test_list": []})]
        change_serialized_population.add(list_temp, "test_list", new_infection)

        a = list_temp[0]["test_list"]
        b = list_temp[1]["test_list"]

        success_ref = list_temp[0]["test_list"] is not list_temp[1]["test_list"]
        list_temp[0]["test_list"][0]["duration"] = 999999
        success_value = not list_temp[0]["test_list"][0]["duration"] == list_temp[1]["test_list"][0]["duration"]
        self.assertTrue(success_ref and success_value, "Error")

    def test_add2(self):
        """ Similar to test above. All the individuals from the subset should get an infection. So the number of
        total infections sould increase by the number of people in this subset. """
        dtk_obj = change_serialized_population.SerializedPopulation(path_dtk_file)

        # count existing infections
        filter_fct = lambda ind: ind["m_age"] < 12000 and ind.suid.id in range(3, 10)
        filtered_individuals = [ind for ind in dtk_obj.nodes[0].individualHumans if filter_fct(ind)]
        number_of_infections = sum([len(ind.infections) for ind in filtered_individuals])

        # create infection and add to individuals
        infection_init = {'suid': {'id': 123}, "duration": 123, "incubation_timer": 456}
        new_infection = change_serialized_population.loadInfection(from_file="infection.json")
        new_infection.update(infection_init.items())

        individual_path = dtk_obj.nodes[0].individualHumans
        change_serialized_population.add(individual_path, "infections", new_infection, filter_fct)

        new_total_number_of_infections = sum(
            [len(ind.infections) for ind in dtk_obj.nodes[0].individualHumans if filter_fct(ind)])

        success = len(filtered_individuals) + number_of_infections == new_total_number_of_infections
        self.assertTrue(success, "Error." + str(
            len(filtered_individuals)) + " individuals should have gotten an infection. There were " + str(
            number_of_infections) + " infections now there are " + str(new_total_number_of_infections) + " infections.")

    def test_get_setPropertyValues_Individual(self):
        dtk_obj = change_serialized_population.SerializedPopulation(path_dtk_file)
        number_of_individuals = len(dtk_obj.nodes[0].individualHumans)

        new_properties = [{"m_age": 7}] * number_of_individuals  # one dict for each individual

        change_serialized_population.setPropertyValues_Individual(0, new_properties, dtk_obj)
        properties = change_serialized_population.getPropertyValues_Individual(0, dtk_obj, "m_age")

        success = sum(properties) == number_of_individuals * 7
        self.assertTrue(success, "Error")

    def test_createIndividual(self):
        New_Age = 3
        dtk_obj = change_serialized_population.SerializedPopulation(path_dtk_file)
        number_individuals = len(dtk_obj.nodes[0].individualHumans)

        copy_ind = dtk_obj.nodes[0].individualHumans[0]
        kwargs = {"m_age": New_Age}
        ind = change_serialized_population.createIndividual(dtk_obj.getNextIndividualSuid(0), copy_ind=copy_ind,
                                                            kwargs=kwargs)
        print(ind)
        dtk_obj.nodes[0].individualHumans.append(ind)

        new_number_individuals = len(dtk_obj.nodes[0].individualHumans)
        success_copy_ind = not copy_ind.m_age == New_Age
        success_added = number_individuals + 1 == new_number_individuals
        success_kwargs = dtk_obj.nodes[0].individualHumans[new_number_individuals - 1]["m_age"] == New_Age
        self.assertTrue(success_added and success_kwargs and success_copy_ind, "Error")


if __name__ == "__main__":
    unittest.main()
