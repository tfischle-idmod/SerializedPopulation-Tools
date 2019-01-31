import matplotlib.pyplot as plt
import random


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


def createDistribution(parameter, number, fct=1):
    distribution = []
    for i in range(number):
        distribution.append({parameter: fct()})
    return distribution