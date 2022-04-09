

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


def calculate_numer_of_wrong_address(k,alpha):
    if k==1:
        return alpha
    return 2*alpha*calculate_numer_of_wrong_address(k-1,alpha) + alpha

    alpha=0.4
    while alpha < 0.8:
        res= calculate_numer_of_wrong_address(2,alpha)
        print("alpha {}:".format(alpha)+  "  r = {}".format(res))
        alpha += 0.05

    for k in range(1,22):
        res = calculate_numer_of_wrong_address(k, 0.5)
        print("k {}:".format(k) + "  r = {}".format(res))

    for k in range(1, 11):
        print ("for prefix {}  p=".format(k) + "{}".format(0.5**(10-k)))


 #   print ("FP for 640 ")

 #   for n in range (1,161):
 #       rate = 640/n
 #       print("rate m/n = {}".format(rate))
 #       print ("for n={} ".format(n) + "FP = {}".format((0.6185) ** rate))


if __name__ == '__main__':
    link = "http://www.somesite.com/details.pl?urn=2344"
    f = urllib.urlopen(link)
    myfile = f.read()
    print(myfile)