import os
import hunspell

GLOBAL_hobj = hunspell.HunSpell('/usr/share/hunspell/nl_NL.dic', '/usr/share/hunspell/nl_NL.aff')
GLOBAL_fuzzylist = []
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fuzzy", "commands.txt")) as f:
    GLOBAL_fuzzylist2 = [line.strip() for line in f.readlines()]
    GLOBAL_fuzzylist = [line for line in GLOBAL_fuzzylist2 if line and not line.startswith("#")]
