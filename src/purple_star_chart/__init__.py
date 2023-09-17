from src.purple_star_chart.constructor_classes import Stem, Branch

# reference tables used throughout
_stem_lookup = {
    'jia': Stem(1, 'jia', 'wood'),
    'yi': Stem(0, 'yi', 'wood'),
    'bing': Stem(1, 'bing', 'fire'),
    'ding': Stem(0, 'ding', 'fire'),
    'wu': Stem(1, 'wu', 'earth'),
    'ji': Stem(0, 'ji', 'earth'),
    'geng': Stem(1, 'geng', 'metal'),
    'xin': Stem(0, 'xin', 'metal'),
    'ren': Stem(1, 'ren', 'water'),
    'gui': Stem(0, 'gui', 'water')
}
_stems = list(_stem_lookup)

_branch_lookup = {
    'zi': Branch(1, 'zi', 'rat', 'water'),
    'chou': Branch(0, 'chou', 'ox', 'earth'),
    'yin': Branch(1, 'yin', 'tiger', 'wood'),
    'mao': Branch(0, 'mao', 'rabbit', 'wood'),
    'chen': Branch(1, 'chen', 'dragon', 'earth'),
    'si': Branch(0, 'si', 'snake', 'fire'),
    'wu': Branch(1, 'wu', 'horse', 'fire'),
    'wei': Branch(0, 'wei', 'goat', 'earth'),
    'shen': Branch(1, 'shen', 'monkey', 'metal'),
    'you': Branch(0, 'you', 'bird', 'metal'),
    'xu': Branch(1, 'xu', 'dog', 'earth'),
    'hai': Branch(0, 'hai', 'pig', 'water')
}
_branches = list(_branch_lookup)
