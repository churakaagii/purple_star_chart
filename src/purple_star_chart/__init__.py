from collections import namedtuple

# commonly used namedtuples
_Stem = namedtuple('Stem', ['name', 'element', 'polarity'])
_Branch = namedtuple('Branch', ['name', 'animal', 'element', 'polarity'])
_Pillar = namedtuple('Pillar', ['type', 'stem', 'branch'])

# reference tables used throughout the class
_stem_lookup = {
    'jia': _Stem('jia', 'wood', 1),
    'yi': _Stem('yi', 'wood', 0),
    'bing': _Stem('bing', 'fire', 1),
    'ding': _Stem('ding', 'fire', 0),
    'wu': _Stem('wu', 'earth', 1),
    'ji': _Stem('ji', 'earth', 0),
    'geng': _Stem('geng', 'metal', 1),
    'xin': _Stem('xin', 'metal', 0),
    'ren': _Stem('ren', 'water', 1),
    'gui': _Stem('gui', 'water', 0)
}

_branch_lookup = {
    'zi': _Branch('zi', 'rat', 'water', 1),
    'chou': _Branch('chou', 'ox', 'earth', 0),
    'yin': _Branch('yin', 'tiger', 'wood', 1),
    'mao': _Branch('mao', 'rabbit', 'wood', 0),
    'chen': _Branch('chen', 'dragon', 'earth', 1),
    'si': _Branch('si', 'snake', 'fire', 0),
    'wu': _Branch('wu', 'horse', 'fire', 1),
    'wei': _Branch('wei', 'goat', 'earth', 0),
    'shen': _Branch('shen', 'monkey', 'metal', 1),
    'you': _Branch('you', 'bird', 'metal', 0),
    'xu': _Branch('xu', 'dog', 'earth', 1),
    'hai': _Branch('hai', 'pig', 'water', 0)
}