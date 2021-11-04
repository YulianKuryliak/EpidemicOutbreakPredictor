import numpy as np
import csv
import pprint


def __get_data(directory, name_of_file):
    #data = np.genfromtxt(directory+ "/" + name_of_file, delimiter=',')[0:]
    data = list(csv.reader(open(directory+ "/" + name_of_file)))
    return data


def __cumulative_data_prob(data):
    data[0]["cumulative"] = data[0]["probability"]
    for i in range(1,len(data)):
        data[i]["cumulative"] = data[i]["probability"] + data[i-1]["cumulative"]


def get_population(dir = "/home/data/projects/ManagingEpidemicOutbreak/Python-v.0.1/datasets/ukraine(16December2020)"):
    data_men = __get_data(dir, "men_total_data.csv")
    data_women = __get_data(dir, "women_total_data.csv")

    amount = 0
    for i in range(1,len(data_men)):
        amount += int(data_men[i][4]) + int(data_women[i][4])
    
    data = []
    for i in range(1,len(data_men)):
        data.append({"age_range": data_men[i][0], "gender": "M", "probability": int(data_men[i][4])/amount, "p_death": float(data_men[i][6])})
        data.append({"age_range": data_women[i][0], "gender": "W", "probability": int(data_women[i][4])/amount, "p_death": float(data_women[i][6])})

    __cumulative_data_prob(data)
    return data

#print('\n'.join(map('\t'.join, get_data("/run/media/fedora_user/31614d99-e16f-45e1-8be5-e21723cf8199/projects/ManagingEpidemicOutbreak/Python-v.0.1/datasets/ukraine(16December2020)", "men_total_data.csv"))))
