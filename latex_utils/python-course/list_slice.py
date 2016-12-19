SAVED_FILE = "python_list_index_exercise.bin"


L = [
    'Apple', 'Google', 'Microsoft',
    'Java', 'Python', 'Ruby', 'PHP',
    'Adam', 'Bart', 'Lisa'
]

L = [e.upper() for e in L]



n = len(L)

import random
import copy

i = 0
question_list = []
while i < 100:
    i += 1
    L_copy = copy.deepcopy(L)
    random.shuffle(L_copy)
    L_copy_split =[]
    L_copy_split.extend([L_copy[:3], L_copy[3:7], L_copy[7:]])

    L_flatten = [item for sublist in L_copy_split for item in sublist]

    # for j, l in enumerate(L_copy_split):
    #     l = [e.title() if e != "PHP" else e for e in l]
    #     L_copy_split[j] = l

    print(repr(L_copy_split))

    question_list.append(L_copy_split)

import pickle
#import dill as pickle
with open(SAVED_FILE, 'wb') as f:
    pickle.dump(question_list, f)

