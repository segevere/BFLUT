

def build_string_from_list(ll):
    str1 = ""
    for ele in ll:
        str1 += "{}".format(ele)
    return str1



def parity_brute_force(x):
    bit = 0
    num_bits = 0
    while x:
        bitmask = 1 << bit
        bit += 1
        if x & bitmask:
            num_bits += 1
        x &= ~bitmask

    return num_bits % 2


def calc_two_parity_bits(bit_val):

    lv = bit_val and 31
    hv = bit_val and 992

    last_bits= str.format("{}{}",parity_brute_force(lv), parity_brute_force(hv))
    print ("last_bits = ", last_bits)
    return last_bits


def calc_single_parity_bits(bit_val):

    last_bits= str.format("{}",parity_brute_force(bit_val))
    print ("parity bit = ", last_bits)
    return last_bits
