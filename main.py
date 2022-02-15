# This is a sample Python script.
import hashlib
import sys
import string
import random

import mmh3
from bitarray import bitarray

import matplotlib
import matplotlib.pyplot as plt

from bflutclass import BfLutClass

def check_load_factor_comparing_to_error_bits():
    bl_lut_object = BfLutClass()
    bl_lut_object.do_error_detection = True
    res = dict()
    for i in range(10):
        print("interation number {}".format(i))
        bl_lut_object.err_correction_bits = i
        bl_lut_object.init()
        res[i] = bl_lut_object.run_test()

    load_factor = dict()
    for i in range(10):
        print(res[i])
        load_factor[i] = res[i]["BF Load Factor "]



    plt.bar(load_factor.keys(),load_factor.values())
    plt.xlabel('error bits')
    plt.ylabel('load factor')
    plt.show()
    return




if __name__ == '__main__':
    bl_lut_object = BfLutClass()
    bl_lut_object.do_error_detection = False
    res = dict()

    for i in range(1, 32):
        bl_lut_object.n_items_to_generate = i
        bl_lut_object.init()
        print("generating items {}".format(i))
        res[i] = bl_lut_object.run_test()

    load_factor = dict()
    keys_found = dict()
    returned_items = dict()
    load:float = dict()
    hit_found_rate:float = dict()
    for i in range(1, 32):
        print(res[i])
        load_factor[i] = res[i]["BF Load Factor "]
        keys_found[i] = res[i]["found in BF"]
        load[i] = float(i/64)
        hit_found_rate[i] = float(res[i]["found in BF"]/res[i]["total words checked"])




    plt.plot(load_factor.keys(),load_factor.values())
    plt.xlabel('words pushed to Bloom Filter')
    plt.ylabel('load factor')
    plt.show()

    plt.bar(keys_found.keys(),keys_found.values())
    plt.xlabel('words pushed to Bloom Filter')
    plt.ylabel('returned items')
    plt.show()

    plt.plot(load.values(), hit_found_rate.values())
    plt.xlabel('load')
    plt.ylabel('hit_found_rate')
    plt.show()


    plt.plot(load.values(), keys_found.values())
    plt.xlabel('load')
    plt.ylabel('returned items')
    plt.show()
