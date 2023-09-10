'''Class for holding BaZi related informaton.
You can initialize it using only a date from the Gregorian calendar if you use
the BaZiDate.from_datetime() method.'''

from lunardate import LunarDate
from attrs import define
from datetime import datetime, date
from collections import namedtuple

# reference tables used throughout the class
_Stem = namedtuple('Stem', ['name', 'element', 'polarity'])
_Branch = namedtuple('Branch', ['name', 'animal', 'element', 'polarity'])
_Pillar = namedtuple('Pillar', ['type', 'stem', 'branch'])

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

@define
class BaZiDate():
    solar_date: datetime
    lunar_date: LunarDate
    year_pillar: _Pillar
    month_pillar: _Pillar
    day_pillar: _Pillar
    hour_pillar: _Pillar

    @classmethod
    def from_datetime(cls, dt):
        '''Intended method for human initialization.
        Takes a gregorian date as a datetime object; does NOT work with
        string input.'''
        # convert to lunar calendar for reference
        ldate = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
        cycle_loc = (dt.year - 3) % 60

        # year init
        ys_loc = (cycle_loc % 10) - 1
        ystem = _stem_lookup[list(_stem_lookup)[ys_loc]]
        yb_loc = (cycle_loc % 12) - 1
        ybranch = _branch_lookup[list(_branch_lookup)[yb_loc]]
        ypillar = _Pillar('year', ystem, ybranch)
        
        # month init
        ms_loc = (cycle_loc % 5) * 2
        mstem = _stem_lookup[list(_stem_lookup)[ms_loc]]
        mbranch = _branch_lookup[list(_branch_lookup)[(ldate.month + 1) % 12]]
        mpillar = _Pillar('month', mstem, mbranch)

        # day init
        days_diff = (dt.date() - date(2000, 1, 7)).days
        if days_diff != 0:
            ds_loc = days_diff % 10
            db_loc = days_diff % 12
            dstem = _stem_lookup[list(_stem_lookup)[ds_loc]]
            dbranch = _branch_lookup[list(_branch_lookup)[db_loc]]
        else:
            dstem = _stem_lookup['jia']
            dbranch = _branch_lookup['zi']
        dpillar = _Pillar('day', dstem, dbranch)

        # hour init
        hs_diff = (dt.hour + 1) // 2 if dt.hour < 23 else 0
        hs_start = (list(_stem_lookup).index(dpillar.stem.name) % 5) * 2
        hstem = _stem_lookup[list(_stem_lookup)[(hs_start + hs_diff) % 10]]
        hbranch = _branch_lookup[list(_branch_lookup)[hs_diff]]
        hpillar = _Pillar('hour', hstem, hbranch)

        return cls(dt, ldate, ypillar, mpillar, dpillar, hpillar)
    
    def pprint(self):
        '''pretty prints bazi results for human use'''
        pillar_fstr = '''
{ptype} PILLAR: {sname} {bname}
  {spol} {selem} {banim}'''
        
        for pillar in [self.year_pillar, self.month_pillar, self.day_pillar, self.hour_pillar]:
            pol = 'yang' if pillar.stem.polarity == 1 else 'yin'
            strvars = {
                'ptype': pillar.type.upper(),
                'sname': pillar.stem.name.capitalize(),
                'bname': pillar.branch.name.capitalize(),
                'spol': pol.capitalize(),
                'selem': pillar.stem.element.capitalize(),
                'banim': pillar.branch.animal.capitalize()
            }
            print(pillar_fstr.format(**strvars))
        print()
