import os
import json


def correct_unicode_to_bin(bad_bytes):
    if bad_bytes.find(b'\\u00') == -1:
        good_bytes = bad_bytes
        return good_bytes
    else:
        i1 = bad_bytes.find(b'\\u00')
        bad_unicode = bad_bytes[i1:i1+12]
        correct_bytes = bad_unicode.decode('unicode_escape').encode('latin1')
        corrected = bad_bytes.replace(bad_unicode, correct_bytes)
        return correct_unicode_to_bin(corrected)


if __name__ == '__main__':

    test_fpath = os.path.join(os.path.split(__file__)[0], '..','..','tmp', 'testlineup.json')
    with open (test_fpath) as jsonf:
        commentary = json.load(jsonf)

    print(correct_unicode_to_bin(bytes(commentary, 'utf-8')))
