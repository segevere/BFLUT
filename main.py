# This is a sample Python script.
import hashlib
import math
import sys
import string
import random

import mmh3
from bitarray import bitarray

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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

    plt.bar(load_factor.keys(), load_factor.values())
    plt.xlabel('error bits')
    plt.ylabel('load factor')
    plt.show()
    return


def check_progressive_load():
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
    load: float = dict()
    hit_found_rate: float = dict()
    for i in range(1, 32):
        print(res[i])
        load_factor[i] = res[i]["BF Load Factor "]
        keys_found[i] = res[i]["found in BF"]
        load[i] = float(i / 64)
        hit_found_rate[i] = float(res[i]["found in BF"] / res[i]["total words checked"])

    plt.plot(load_factor.keys(), load_factor.values())
    plt.xlabel('words pushed to Bloom Filter')
    plt.ylabel('load factor')
    plt.show()

    plt.bar(keys_found.keys(), keys_found.values())
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


def check_BF_MBF(num_of_items, fault_positive_presents):
    bl_lut_object = BfLutClass(num_of_items, fp_prob=fault_positive_presents / 100)
    bl_lut_object.do_error_detection = False
    bl_lut_object.check_absent_words = False

    bl_lut_object.blf_hash_count = 2
    bl_lut_object.size_as_items_count = False  # let BF to calculate the size

    n_iterations = 100
    res = dict()

    keys_found_rate: float = dict()

    sum_num = 0
    iterations = 0
    max_rate = 0

    for i in range(1, n_iterations):
        bl_lut_object.init()
        res[i] = bl_lut_object.run_test()
        keys_found_rate[i] = res[i]["found in BF"] / bl_lut_object.n_items_to_generate
        if keys_found_rate[i] > max_rate:
            max_rate = keys_found_rate[i]

        sum_num += res[i]["found in BF"]
        iterations += 1

    sum_num /= iterations

    plt.plot(keys_found_rate.keys(), keys_found_rate.values())
    plt.xlabel('iteration')
    plt.ylabel('ratio')
    plt.title('over hit per iteration')
    plt.text(1, max_rate, 'n words {}'.format(bl_lut_object.n_items_to_generate) + 'average {}'.format(
        sum_num / bl_lut_object.n_items_to_generate))
    # plt.show()

    load_factor = dict()
    found_in_bf_dict = dict()
    lf_sum: float = 0
    iterations = 0
    av_sum = 0
    load_factor_max = 0
    load_factor_mbf = dict()
    for i in range(1, n_iterations):
        lf = res[i]["BF Load Factor "]
        found_in_bf = res[i]["found in BF"]
        load_factor_mbf[i] = res[i]["multi BF av load factor"]
        av_sum += found_in_bf
        found_in_bf_dict[i] = found_in_bf
        load_factor[i] = lf
        if lf > load_factor_max:
            load_factor_max = lf
        lf_sum += lf
        iterations += 1

    av_found_in_bf = av_sum / iterations
    lf_av: float = lf_sum / iterations

    plt.plot(load_factor.keys(), load_factor.values(), 'r', load_factor_mbf.keys(), load_factor_mbf.values(), 'b')
    plt.xlabel('iteration')
    plt.ylabel('load_factor')
    plt.title('load factor per iteration')
    plt.text(1, load_factor_max, 'n words {}'.format(bl_lut_object.n_items_to_generate) + ' average {}'.format(lf_av))
    # plt.show()

    for x in res:
        print(res[x])

    import pandas as pd

    data = []
    for i, key in enumerate(res.keys()):
        try:
            data.append((key
                         , res[key]['BF Load Factor ']
                         , res[key]['multi BF av load factor']
                         , res[key]['found in multi BF']
                         , res[key]['found in BF']
                         ))
        # if no entry, skip
        except:
            pass

    print("-------------------------------------------------------------------")
    print("Testing {} Items ".format(num_of_items) + "in fixed size BF {}".format(bl_lut_object.bf_initiation_size))

    print("Single Bloom Filter")
    print("-------------------")
    print("Size of bit array  {}".format(res[1]['BF bit array size ']))
    print("Number of hashes    {}".format(res[1]['BF hash_count']))
    print("")
    print("Multiple Bloom Filters")
    print("----------------------")
    print("Size of bit array  {}".format(res[1]['multi BF bit array size']))
    print("Number of hashes   {}".format(res[1]['multi BF hash count']))
    print("")

    df = pd.DataFrame(data=data, columns=['test', 'BF Load Factor ', 'multi BF av load factor', 'found in multi BF',
                                          'found in BF'])

    # print(df)
    check_BF_MBF_dict = dict()
    check_BF_MBF_dict['SBF bit Array'] = res[1]['BF bit array size ']
    check_BF_MBF_dict['SBF Hashes'] = res[1]['BF hash_count']

    check_BF_MBF_dict['MBF bit Array'] = res[1]['multi BF bit array size']
    check_BF_MBF_dict['MBF Hashes'] = res[1]['multi BF hash count']

    check_BF_MBF_dict['mean of SBF Items Found'] = df.mean()['found in BF']
    check_BF_MBF_dict['mean of SBF Load Factor'] = df.mean()['BF Load Factor ']
    check_BF_MBF_dict['mean of MBF items found'] = df.mean()['found in multi BF']
    check_BF_MBF_dict['mean of MBF Load Factor'] = df.mean()['multi BF av load factor']

    check_BF_MBF_dict['SD of SBF Items Found'] = df.std()['found in BF']
    check_BF_MBF_dict['SD of SBF Load Factor'] = df.std()['BF Load Factor ']
    check_BF_MBF_dict['SD of MBF items found'] = df.std()['found in multi BF']
    check_BF_MBF_dict['SD of MBF Load Factor'] = df.std()['multi BF av load factor']

    return check_BF_MBF_dict


def check_BF_MBF_test():
    # this test compares single instance of BF agains Multi instance
    res = dict()

    for percent in range(1, 3):
        res[percent] = check_BF_MBF(16, percent)

    print("1-50 % run for 16 elements")
    print("--------------------------")

    for item in res:
        print("16 elements in {} FP percents:".format(item) + str(res[item]))


def check_static_bf(items_num=16, k=1, m=460):
    bl_lut_object = BfLutClass(num_of_items=items_num,
                               static_allocation=True,
                               num_of_hashes_in_static_allocation=k,
                               bf_fixed_size=m)

    n_iterations = 100
    res = dict()

    keys_found_rate: float = dict()

    sum_num = 0
    iterations = 0
    max_rate = 0

    for i in range(1, n_iterations):
        bl_lut_object.init()
        res[i] = bl_lut_object.run_test()
        keys_found_rate[i] = res[i]["found in BF"] / bl_lut_object.n_items_to_generate
        if keys_found_rate[i] > max_rate:
            max_rate = keys_found_rate[i]

        sum_num += res[i]["found in BF"]
        iterations += 1

    sum_num /= iterations

    #plt.plot(keys_found_rate.keys(), keys_found_rate.values())
    #plt.xlabel('iteration')
    #plt.ylabel('ratio')
    #plt.title('over hit per iteration')
    #plt.text(1, max_rate, 'n words {}'.format(bl_lut_object.n_items_to_generate) + 'average {}'.format(
        #sum_num / bl_lut_object.n_items_to_generate))
    # plt.show()

    load_factor = dict()
    found_in_bf_dict = dict()
    lf_sum: float = 0
    iterations = 0
    av_sum = 0
    load_factor_max = 0
    load_factor_mbf = dict()
    for i in range(1, n_iterations):
        lf = res[i]["BF Load Factor "]
        found_in_bf = res[i]["found in BF"]
        load_factor_mbf[i] = res[i]["multi BF av load factor"]
        av_sum += found_in_bf
        found_in_bf_dict[i] = found_in_bf
        load_factor[i] = lf
        if lf > load_factor_max:
            load_factor_max = lf
        lf_sum += lf
        iterations += 1

    av_found_in_bf = av_sum / iterations
    lf_av: float = lf_sum / iterations

    #plt.plot(load_factor.keys(), load_factor.values(), 'r', load_factor_mbf.keys(), load_factor_mbf.values(), 'b')
    #plt.xlabel('iteration')
    #plt.ylabel('load_factor')
    #plt.title('load factor per iteration')
    #plt.text(1, load_factor_max, 'n words {}'.format(bl_lut_object.n_items_to_generate) + ' average {}'.format(lf_av))
    # plt.show()

    for x in res:
        print(res[x])

    import pandas as pd

    data = []
    for i, key in enumerate(res.keys()):
        try:
            data.append((key
                         , res[key]['BF Load Factor ']
                         , res[key]['multi BF av load factor']
                         , res[key]['found in multi BF']
                         , res[key]['found in BF']
                         ))
        # if no entry, skip
        except:
            pass

    print("-------------------------------------------------------------------")
    print("Testing {} Items ".format(items_num) + "in {} Fault positive rate".format(bl_lut_object.bf_initiation_size))

    print("Single Bloom Filter")
    print("-------------------")
    print("Size of bit array  {}".format(res[1]['BF bit array size ']))
    print("Number of hashes    {}".format(res[1]['BF hash_count']))
    print("")
    print("Multiple Bloom Filters")
    print("----------------------")
    print("Size of bit array  {}".format(res[1]['multi BF bit array size']))
    print("Number of hashes   {}".format(res[1]['multi BF hash count']))
    print("")

    df = pd.DataFrame(data=data, columns=['test', 'BF Load Factor ', 'multi BF av load factor', 'found in multi BF',
                                          'found in BF'])

    print(df.mean())
    check_BF_MBF_dict = dict()
    check_BF_MBF_dict['SBF bit Array'] = res[1]['BF bit array size ']
    check_BF_MBF_dict['SBF Hashes'] = res[1]['BF hash_count']

    check_BF_MBF_dict['MBF bit Array'] = res[1]['multi BF bit array size']
    check_BF_MBF_dict['MBF Hashes'] = res[1]['multi BF hash count']

    check_BF_MBF_dict['mean of SBF Items Found'] = df.mean()['found in BF']
    check_BF_MBF_dict['mean of SBF Load Factor'] = df.mean()['BF Load Factor ']
    check_BF_MBF_dict['mean of MBF items found'] = df.mean()['found in multi BF']
    check_BF_MBF_dict['mean of MBF Load Factor'] = df.mean()['multi BF av load factor']

    check_BF_MBF_dict['SD of SBF Items Found'] = df.std()['found in BF']
    check_BF_MBF_dict['SD of SBF Load Factor'] = df.std()['BF Load Factor ']
    check_BF_MBF_dict['SD of MBF items found'] = df.std()['found in multi BF']
    check_BF_MBF_dict['SD of MBF Load Factor'] = df.std()['multi BF av load factor']

    return check_BF_MBF_dict


def check_inc_static_bf():
    # this test compares single instance of BF agains Multi instance
    res = dict()
    bit_array_size_dict: float = dict()
    address_fp_rate_dict: float = dict()


    for n in range(1, 49):
        k = 2
        m = int(k * n * 10 / math.log(2))
        res[n] = check_static_bf(n, k=k, m=m)
        bit_array_size_dict[n] = res[n]["SBF bit Array"]
        address_fp_rate_dict[n] = res[n]["mean of MBF items found"]/n

    print("1-64 elements run in static BF")
    print("--------------------------")

    for item in res:
        print("{} element(s):".format(item) + str(res[item]))

    plt.plot(bit_array_size_dict.keys(), bit_array_size_dict.values(),'b')
    plt.xlabel('n')
    plt.ylabel('m')
    plt.title('m(n)')
    plt.show()

    plt.plot(address_fp_rate_dict.keys(), address_fp_rate_dict.values(),'b')
    plt.xlabel('n')
    plt.ylabel('found/actual')
    plt.title('address_fp_rate')
    plt.show()


def calculate_numer_of_wrong_address(k,alpha):
    if k==0:
        return alpha
    return 2*alpha*calculate_numer_of_wrong_address(k-1,alpha) + alpha


def check_inc_static_bf_k_iteration():
    # this test compares single instance of BF agains Multi instance
    res = dict()
    bit_array_size_dict: float = dict()
    MBF_bit_array_size_dict: float = dict()
    address_fp_rate_dict: float = dict()
    MBF_address_fp_rate_dict: float = dict()
    FP_probabilty: float = dict()
    MBF_FP_probabilty: float = dict()

    m_divide_by_n_rate: float  = dict()
    r = dict()
    MBF_r = dict()



    for k in range(1, 9):
        n = 16
        m = int(k * n * 10 / math.log(2))

        res[k] = check_static_bf(n, k=k, m=m)
        MBF_m = m/10
        MBF_rate: float = MBF_m / n

        rate: float = m / n / 10
        bit_array_size_dict[k] = res[k]["SBF bit Array"]
        MBF_bit_array_size_dict[k] = res[k]["MBF bit Array"]
        address_fp_rate_dict[k] = res[k]["mean of SBF Items Found"]/n - 1
        MBF_address_fp_rate_dict[k] = res[k]["mean of MBF items found"]/n - 1
        FP_probabilty[k] = 0.6185 ** rate
        MBF_FP_probabilty[k] = 0.6185 ** MBF_rate
        alpha = (res[k]['mean of MBF Load Factor']) ** k
        MBF_alpha = (res[k]['mean of SBF Load Factor']) ** k
        m_divide_by_n_rate[k] = rate
        r[k] = calculate_numer_of_wrong_address(10,alpha)
        MBF_r[k] = calculate_numer_of_wrong_address(1, MBF_alpha)



    print("k=1-8 run for 16 elements (*10)")
    print("--------------------------")

    for item in res:
        print("{} element(s):".format(item) + str(res[item]))

    #plt.plot(bit_array_size_dict.keys(), bit_array_size_dict.values(),'b')
    #plt.xlabel('k')
    #plt.ylabel('m')
    #plt.title('m(k)')
    #plt.show()

    print(address_fp_rate_dict)
    print(FP_probabilty)
    print(r)

    fig, ax = plt.subplots()
    red_patch = mpatches.Patch(color='red', label='FP Probability')
    blue_patch = mpatches.Patch(color='blue', label='actual FP Rate (found/actual)')
    green_patch = mpatches.Patch(color='green', label='calculated rate wrt real alpha')
    black_patch = mpatches.Patch(color='black', label='m/n rate')
    ax.legend(handles=[red_patch,blue_patch,green_patch])



    plt.plot( address_fp_rate_dict.keys(),address_fp_rate_dict.values(),'b',
              FP_probabilty.keys(),FP_probabilty.values(),'r',
              r.keys(),r.values(), 'g',
    #         m_divide_by_n_rate.keys(), m_divide_by_n_rate.values(), 'k--'
              )
    plt.xlabel('number of hashes')
    plt.title('Num. of Hashes  (k) , m (bit array size) = f(num_of_item,k)')
    plt.show()

    fig, ax = plt.subplots()
    blue_patch = mpatches.Patch(color='blue', label='MBF actual FP rate')
    red_patch = mpatches.Patch(color='red', label='MBF FP probability')
    green_patch = mpatches.Patch(color='green', label='calculated rate wrt real alpha')
    ax.legend(handles=[red_patch, blue_patch,green_patch])

    plt.plot(MBF_address_fp_rate_dict.keys(), MBF_address_fp_rate_dict.values(), 'b',
             MBF_FP_probabilty.keys(), MBF_FP_probabilty.values(), 'r',
             MBF_r.keys(), MBF_r.values(), 'g',
             )
    plt.xlabel('Number of Hushes ')
    plt.title('MFB  Num. of Hashes  (k) , m (bit array size) = f(n,k)')
    plt.show()


    plt.plot(FP_probabilty.keys(), FP_probabilty.values(),'k--')
    plt.xlabel('k')
    plt.ylabel('rate')
    plt.title(' 0.6185 ** n/m')
    plt.show()



if __name__ == '__main__':

    #check_inc_static_bf_k_iteration()
    check_inc_static_bf()