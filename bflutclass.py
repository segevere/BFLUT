import hashlib

from BLF import BloomFilter
from GeneralMethods import calc_two_parity_bits, calc_single_parity_bits
from hashtable import HashTable



class BfLutClass:
    def __init__(self):
        self.print_bloom_factor_results = False
        self.length_of_recursion = None
        self.do_error_detection = False
        self.err_correction_bits = 1
        self.dual_parity_bits_error_detection = False  # add 2 bits of parity for every 5 bits
        self.single_parity_bits_error_detection = False  # add single bit of parity for every 5 bits
        self.word_length = 32
        self.bfluf_k_items_to_init_tables = 16  # number of items to be added
        self.n_items_to_generate = 16  # number of items to be added

        self.bfluf_m_address_bits:int = 10  # number of bits (address) Assume an address requires m bits
        self.fp_prob = 0.382  # Fault Positive 0.382 leads to 320 bitarray size
        self.ht_initial_size = self.bfluf_k_items_to_init_tables * 2
        self.print_tables = False
        self.print_HT = False
        self.check_absent_words = False


        # bf_initiation_siz : Number of items expected to be stored in bloom filter
        self.bf_initiation_size = self.bfluf_k_items_to_init_tables * self.bfluf_m_address_bits * 2
        # fp_prob : False Positive probability in decimal
        # Fault Positive 0.382 leads to 320 bitarray size and single hash operation
        self.fp_prob = 0.382
        self.ht_initial_size = self.bfluf_k_items_to_init_tables * 2
        self.print_tables = False
        self.print_HT = False
        self.check_absent_words = True
        self.word_present = list()
        self.word_absent = list()

        self.bloomf = BloomFilter(self.bf_initiation_size, self.fp_prob)
        self.hashTable = HashTable(self.ht_initial_size)
        self.generateWords()
        self.resultDict = set()

    def init(self):
        if self.do_error_detection is True:
            self.length_of_recursion = self.bfluf_m_address_bits + self.err_correction_bits + 1
        elif self.dual_parity_bits_error_detection is True:
            self.length_of_recursion = self.bfluf_m_address_bits + 3
        elif self.single_parity_bits_error_detection is True:
            self.length_of_recursion = self.bfluf_m_address_bits + 2
        else:
            self.length_of_recursion = self.bfluf_m_address_bits + 1

        self.bloomf.__init__(self.bf_initiation_size, self.fp_prob)
        self.hashTable.__init__(self.ht_initial_size)

        self.word_present = list()
        self.word_absent = list()

        self.generateWords()
        # generating words lists

        self.resultDict.__init__()




        # end of init

    def generateWords(self):
        f = open("keyFile.txt", "r")
        for x in range(self.n_items_to_generate):
            word = f.readline()
            # print("add to present = " + word)
            self.word_present.append(word)
            word = f.readline()
            # print("add to absent = " +  word)
            self.word_absent.append(word)

    def get_last_bits_of_sha3_hash(self, bits_val):
        hash_val_int = hashlib.sha3_256(bytearray(bits_val.encode()))
        len_of_hex = hash_val_int.hexdigest().__len__()
        hash_val_bit = "{:b}".format(int(hash_val_int.hexdigest()[len_of_hex - 10:len_of_hex], base=16))
        last_bits = hash_val_bit[hash_val_bit.__len__() - self.err_correction_bits:hash_val_bit.__len__()]
        return last_bits

    def add2Bloom(self, key, index):
        # temp = format(index, "{0:b}")
        bin_val = "{:010b}".format(index)
        #   print("bin_val="+bin_val)
        if self.do_error_detection is True:
            last_bits = self.get_last_bits_of_sha3_hash(bin_val)
            print("adding to bloom = " + bin_val + " CRC " + last_bits)
            bin_val += last_bits
            for i in range(1, self.bfluf_m_address_bits + self.err_correction_bits + 1):
                to_bloom = str(key) + bin_val[0:i]
                self.bloomf.add(to_bloom)
        #           print("Add to Bloom "+to_bloom )
        elif self.dual_parity_bits_error_detection is True:
            last_bits = calc_two_parity_bits(index)
        #   print("adding to bloom = " + bin_val + " CRC " + last_bits)
            bin_val += last_bits
            for i in range(1, self.bfluf_m_address_bits + 2 + 1):
                to_bloom = str(key) + bin_val[0:i]
                self.bloomf.add(to_bloom)

        elif self.single_parity_bits_error_detection is True:
            last_bits = calc_single_parity_bits(index)
        #   print("adding to bloom = " + bin_val + " parity " + last_bits)
            bin_val += last_bits
            for i in range(1, self.bfluf_m_address_bits + 2):
                to_bloom = str(key) + bin_val[0:i]
                self.bloomf.add(to_bloom)
        else:
            for i in range(1, self.bfluf_m_address_bits + 1):
                to_bloom = str(key) + bin_val[0:i]
                self.bloomf.add(to_bloom)
         #      print("Add to Bloom " + to_bloom)

    def fillHashandBloom(self):
        for x in range(self.n_items_to_generate):
            self.hashTable.set(self.word_present[x], self.word_present[x])
            self.add2Bloom(self.word_present[x], x)

    def breakWordandAddtoResultList(self, word):
        key = word[0:self.word_length - 1]
        index = word[self.word_length:self.word_length + self.bfluf_m_address_bits - 1]

        if self.do_error_detection is True:
            index_with_crc = word[self.word_length + 1:self.word_length + self.bfluf_m_address_bits + self.err_correction_bits + 1]
            print("index_with_crc = " + index_with_crc)
            index = index_with_crc[0:self.bfluf_m_address_bits]
            crc = index_with_crc[self.bfluf_m_address_bits:self.bfluf_m_address_bits + self.err_correction_bits]
            crc_comp = self.get_last_bits_of_sha3_hash(index)

            if crc == crc_comp:
                print("adding to results " + index + " crc = " + crc)
                self.resultDict.add((key, index))
            else:
                print("Not added  to results " + index + " crc = " + crc)

        elif self.dual_parity_bits_error_detection is True:
            index_with_crc = word[self.word_length + 1:self.word_length + self.bfluf_m_address_bits + 2 + 1]
            print("index_with_crc = " + index_with_crc)
            index = index_with_crc[0:self.bfluf_m_address_bits]
            crc = index_with_crc[self.bfluf_m_address_bits:self.bfluf_m_address_bits + 2]
            crc_comp = calc_two_parity_bits(int(crc))
            if crc == crc_comp:
                print("adding to results " + index + " crc = " + crc)
                self.resultDict.add((key, index))
            else:
                print("Not added  to results " + index + " crc = " + crc)

        elif self.single_parity_bits_error_detection is True:
            index_with_crc = word[self.word_length + 1:self.word_length + self.bfluf_m_address_bits + 2]
            print("index_with_crc = " + index_with_crc)
            index = index_with_crc[0:self.bfluf_m_address_bits]
            crc = index_with_crc[self.bfluf_m_address_bits:self.bfluf_m_address_bits + 1]
            crc_comp = calc_single_parity_bits(int(crc))
            if crc == crc_comp:
                print("adding to results " + index + " crc = " + crc)
                self.resultDict.add((key, index))
            else:
                print("Not added  to results " + index + " crc = " + crc)
        else:
            self.resultDict.add((key, index))

    # searching for word by adding bit after bit
    def checkIfInBloom(self, word, i):
        if i == self.length_of_recursion:
            self.breakWordandAddtoResultList(word)
            return
        ask_bloom_plus_0 = word + "0"
        ask_bloom_plus_1 = word + "1"
        if self.bloomf.check(ask_bloom_plus_0):
            self.checkIfInBloom(ask_bloom_plus_0, i + 1)
        if self.bloomf.check(ask_bloom_plus_1):
            self.checkIfInBloom(ask_bloom_plus_1, i + 1)

    def check_absent(self):
        if self.check_absent_words is False:
            return 0
        ht_found_values: int = 0
        for word in self.word_absent:
#           print("checking absent if exist in Bloom " + word)
            self.checkIfInBloom(word, 1)
            try:
                value_found = self.hashTable.get(word)
                ht_found_values += 1
            except KeyError:
                pass

        absent_words_founded_in_bf = self.resultDict.__len__()
        print("\nchecking existence of absent words ")
        print("---------------------------------- ")
        print("total Words Checked: {} ".format(self.word_absent.__len__()))
        print("Found in HT: {}".format(ht_found_values))
        print("Found in BF: {}".format(absent_words_founded_in_bf))

        if absent_words_founded_in_bf > 0:
            print("Clearing Results ")
            self.resultDict.clear()

        return absent_words_founded_in_bf


    def printTable(self):
        if self.print_tables is False:
            return
        print("\nelement info ")
        print("------------------------ ")
        print("type of element {}".format(type(self.word_present[0])))
        print("size of element in bits {}".format(len(self.word_present[0]) * 8))

        print("\n Bloom Filter content ")
        print("------------------------ ")
        print(self.resultDict)

        print("\n Bloom Filter content ")
        print("------------------------ ")
        print(self.bloomf.bit_array)

        print("\nHash Table content  ")
        print("------------------------ ")
        for x in self.hashTable.container:
            print(x)
        # + str(len * word_length * 8))






    def PrintHashTable(self):
        if self.print_HT is True:
            print("\nHash Table Information ")
            print("------------------------ ")
            print("Hash container size  = {}".format(self.hashTable.container_size))
            print("num_of_filled_items = {}".format(self.hashTable.num_of_filled_items()))
            print("Hash container sizeof (in bytes) = {}".format(self.hashTable.container.__sizeof__()))
            print("Hash container sizeof  (in bits computed)= {}".format(self.hashTable.container.__sizeof__() * 8))
            print("Hash container computed size with respect to items size = {}".format(
                self.hashTable.container_size * self.word_length))
            print("Hash container computed size with respect to items size (bits) = {}".format(
                self.hashTable.container_size * self.word_length * 8))

    def PrintReport(self):
        print("Global Vars ")
        print("------------")
        print("Word Length  {} ".format(self.word_length))
        print("Number of Items to Init table  {} ".format(self.bfluf_k_items_to_init_tables))
        print("Number of Items generated  {} ".format(self.n_items_to_generate))
        print("size of address in bits  {} ".format(self.bfluf_m_address_bits))

    def run_test(self):

        res_dict = dict()

        res_dict["Word Length"] = self.word_length
        res_dict["Items Num"]   = self.bfluf_k_items_to_init_tables
        res_dict["Bits Num"]    = self.bfluf_m_address_bits
        res_dict["fp_prob"]    = self.fp_prob

        self.fillHashandBloom()

        res_dict["Absents Found"] = self.check_absent() #inspect

        ht_found_values = 0
        self.resultDict.clear()
        for word in self.word_present:
            self.checkIfInBloom(word, 1) # if in bloom updates resultDict
            try:
                value_found = self.hashTable.get(word)
                ht_found_values = ht_found_values + 1
            except KeyError:
                pass

        res_dict["found in BF"] = self.resultDict.__len__()
        res_dict["total words checked"]=self.word_present.__len__()
        res_dict["Found in HT"]= ht_found_values
        res_dict["Found in BF"]=self.resultDict.__len__()
        res_dict["BF bl_initiation_size"] = self.bf_initiation_size
        res_dict["BF bit array size "] = self.bloomf.size
        res_dict["BF Load Factor "] = self.bloomf.get_load_factor()
        res_dict["BF hash_count"] = self.bloomf.hash_count


        self.PrintBloomFilterResult(ht_found_values)


        self.PrintHashTable()

        self.printTable()




        return res_dict

    def PrintBloomFilterResult(self,ht_found_values):
        if self.print_bloom_factor_results is not True:
            return

        present_words_founded_in_bf = self.resultDict.__len__()
        print("\n checking existence of present words ")
        print("---------------------------------- ")
        print("total Words Checked: {} ".format(self.word_present.__len__()))
        print("Found in HT: {}".format(ht_found_values))
        print("Found in BF: {}".format(present_words_founded_in_bf))

        print("\n Bloom Filter Information ")
        print("------------------------ ")
        print("BL number of items requested : {}".format(self.bf_initiation_size))
        print("BL calculated size of bit array  : {}".format(self.bloomf.get_size(self.bf_initiation_size, self.fp_prob)))
        print("Final Size of bit array: {}".format(self.bloomf.size))
        print("load factor= {}".format(self.bloomf.get_load_factor()))
        print("hash_count= {}".format(self.bloomf.hash_count))