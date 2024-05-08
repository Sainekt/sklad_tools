# barcods generator
import os
from random import randint

from django.conf import settings

file_path = os.path.join(settings.BASE_DIR, 'utils', 'ozon', 'barcods.txt')


def get_set_barcods():
    barcods = set()
    with open(file_path, 'r') as file_read:
        for i in file_read.readlines():
            barcods.add(i.rstrip())
    return barcods


def barcode_gen(barcods):
    barcod = 'ZD' + str(randint(23000000, 23999999))
    while barcod in barcods:
        barcod = 'ZD' + str(randint(23000000, 23999999))
    barcods.add(barcod)
    write_new_barcod(barcod)
    return barcod


def write_new_barcod(new_barcod):
    with open(file_path, 'a') as file_write:
        file_write.write(new_barcod + '\n')


barcode_set = get_set_barcods()
