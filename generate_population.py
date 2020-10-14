import emod_api.serialization.SerializedPopulation
import copy
import random
import emod_api.serialization.dtkFileSupport as dfs


def create_synthetic_pop( input_dtk_file, new_total_pop, new_num_infected, new_dtk_file ):
    ser_pop_in = emod_api.serialization.SerializedPopulation.SerializedPopulation( input_dtk_file )
    ser_pop_temp = copy.deepcopy(ser_pop_in)

    # delete all individuals
    del ser_pop_in.nodes[0].individualHumans[:]
    del ser_pop_in.nodes[0].home_individual_ids[:]

    infected_individuals = [i for i in ser_pop_temp.nodes[0]['individualHumans'] if i['m_is_infected']]
    random_infected = random.sample(infected_individuals, new_num_infected)

    not_infected_individuals = [i for i in ser_pop_temp.nodes[0]['individualHumans'] if not i['m_is_infected']]
    num_not_infected = new_total_pop - new_num_infected
    random_not_infected = random.choices(not_infected_individuals, k=num_not_infected)  # Random sampling with replacement

    # append infected and not infected individuals
    for ind in random_infected:
        ind.suid = ser_pop_in.get_next_individual_suid(0)
        ser_pop_in.nodes[0].individualHumans.append(ind)
        ser_pop_in.nodes[0].home_individual_ids.append({'key': ind.suid['id'], 'value': ind.suid})

    for ind in random_not_infected:
        ind.suid = ser_pop_in.get_next_individual_suid(0)
        ser_pop_in.nodes[0].individualHumans.append(ind)
        ser_pop_in.nodes[0].home_individual_ids.append({'key': ind.suid['id'], 'value': ind.suid})

    # save
    ser_pop_in.write(new_dtk_file)
    
dtk_in = "C://Users//tfischle//Desktop//serialized_test//serialized_test//state-01480.dtk"
dtk_out = "C://Users//tfischle//Desktop//serialized_test//serialized_test//out.dtk"
create_synthetic_pop(dtk_in, 10, 5, dtk_out)
