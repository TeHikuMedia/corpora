import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import features

GREEN    = "\033[01;32m"
RED      = "\033[01;31m"
YELLOW   = "\033[01;33m"
C_NORMAL = "\033[00m"

def format_features(c):
    a = set()
    colours = ['', RED, YELLOW, GREEN]

    for k, v in c.most_common():
        #a.append(' %s%s' % (colours[len(k)], k))
        if (v > 1):
            k = '%s*%d' % (k, v)
        a.add(k)
    return set(a)


class TestFeaturesImport(unittest.TestCase):
    def test_mi_import_success(self):
        f = features.import_finder('mi')
        for s, answer in [
                ("nananananananānānanana na",
                 {"na*12", "n*12", "a*10", "an*10", "ana*10", "nan*8", "ā*2",
                  "aa*2", "naa*2", "aan*2", "«n*2", "na»*2", "a»*2", "«na*2",
                  " "}
                ),
                ("ko wai au?",
                 {" *2", "ai", "«ko", "au", "«au", "«a", "ȧ", "ai»", "«k",
                  "wai", "o»", "u»", "«w", "«wa", "i»", "wa", "ä", "k", "ko",
                  "o", "ko»", "w", "au»"}),
                ("", set()),
                ("e", {"«e»", "e", "e»", "«e"}),
                ("E ahu pēhea ana koe?! @#@!$#@%$#^ AUE",
                 {" *5", "a*4", "«a*3", "e»*3", "e*3", "a»*2", "h*2", "oe»",
                  "eh", "ee", "ah", "«ah", "ea", "«an", "an", "ē", "au",
                  "«au", "ahu", "hu»", "aue", "«e", "«k", "na", "koe",
                  "«ko", "«p", "«pe", "u»", "pee", "hea", "pe", "hu", "ue",
                  "œ", "«e»", "na»", "ue»", "he", "ä", "k", "ko", "ea»", "n",
                  "p", "u", "eeh", "ana", "ehe", "oe"}),
                ("ko Mare tōku ingoa",
                 {" *3", "a*2", "k*2", "o*2", "ŋoa", "ko", "«ko", "ar",
                  "are", "u»", "to", "«k", "«i", "«m", "oa", "«iŋ", "re",
                  "iŋ", "«to", "o»", "too", "«t", "oo", "mar", "oku", "ok",
                  "ŋo", "ŋ", "ō", "ook", "e»", "ma", "a»", "ku»", "re»", "e",
                  "«ma", "i", "oa»", "m", "ko»", "r", "u", "t", "ku", "iŋo"}),
                ("ko Iha tōku ingoa 123", # the 123 is ignored
                 {" *3", "«i*2", "a»*2", "a*2", "i*2", "k*2", "o*2",
                  "«iŋ", "ŋoa", "oa»", "ih", "«ko", "«ih", "oa",
                  "iha", "u»", "«k", "iŋ", "to", "o»",
                  "too", "«t", "oo", "oku", "ŋo", "ŋ", "ō", "ook",
                  "«to", "ku»", "ha", "ok", "h", "ko",
                  "ko»", "ha»", "u", "t", "ku", "iŋo"}),
                ("aeiouāēīōū hīkōmānūngīpērītēwāwhī",
                 {"ii*5", "ī*5", "ā*3", "ee*3", "aa*3", "ē*3", "ei*2", "ō*2",
                  "oo*2", "ou*2", "" "uu*2", "ae*2", "io*2", "ū*2", "uu»",
                  "ite", " ", "te", "ri", "ŋi", "uŋ", "hii", "h",
                  "eew", "eer", "p", "eei", "t", "aei", "aee", "oua", "nuu",
                  "tee", "ew", "ouu", "er", "ŋii", "pee", "ŋ", "oma", "wa",
                  "iko", "ioo", "om", "k", "w", "fii", "«ae", "ipe",
                  "«a", "koo", "«h", "waa", "pe", "iit", "i»", "iip", "oom",
                  "oou", "hi", "iio", "iik", "aae", "aaf", "ma", "f", "aan",
                  "ik", "n", "r", "eii", "ua", "eri", "eio", "uŋi", "af",
                  "ip", "it", "ii»", "an", "anu", "rii", "uaa", "afi", "u»",
                  "i", "nu", "iou", "m", "maa", "«hi", "fi", "æ", "ko",
                  "uuŋ", "ö", "ewa"}),
        ]:
            c = f(s)
            self.assertEqual(format_features(c), answer)

    def test_mi_import_fail(self):
        f = features.import_finder('mi')
        for s in ['esdf velifont', # bad bad bad
                  'ko Mare [Murray] tōku ingoa', # bad word (Murray)
                  'ko Murray tōku ingoa', # bad word (Murray)
                  'ko Iha tōku ing', # bad word ending ("ing").
        ]:
            c = f(s)
            print(c)
            if c:
                cc = format_features(c)
                self.fail("incorrectly parsed %s: %s" % (s, cc))


    def test_missing_import(self):
        f = features.import_finder('missing')



if __name__ == '__main__':
    unittest.main()
