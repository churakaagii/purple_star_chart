from lunardate import LunarDate
from attrs import define
from datetime import datetime, date
from collections import namedtuple

Stem = namedtuple('Stem', ['name', 'element', 'polarity'])
Branch = namedtuple('Branch', ['name', 'animal', 'element', 'polarity'])
Pillar = namedtuple('Pillar', ['stem', 'branch'])

_stem_lookup = {
    'jia': Stem('jia', 'wood', 1),
    'yi': Stem('yi', 'wood', 0),
    'bing': Stem('bing', 'fire', 1),
    'ding': Stem('ding', 'fire', 0),
    'wu': Stem('wu', 'earth', 1),
    'ji': Stem('ji', 'earth', 0),
    'geng': Stem('geng', 'metal', 1),
    'xin': Stem('xin', 'metal', 0),
    'ren': Stem('ren', 'water', 1),
    'gui': Stem('gui', 'water', 0)
}

_branch_lookup = {
    'zi': Branch('zi', 'rat', 'water', 1),
    'chou': Branch('chou', 'ox', 'earth', 0),
    'yin': Branch('yin', 'tiger', 'wood', 1),
    'mao': Branch('mao', 'rabbit', 'wood', 0),
    'chen': Branch('chen', 'dragon', 'earth', 1),
    'si': Branch('si', 'snake', 'fire', 0),
    'wu': Branch('wu', 'horse', 'fire', 1),
    'wei': Branch('wei', 'goat', 'earth', 0),
    'shen': Branch('shen', 'monkey', 'metal', 1),
    'you': Branch('you', 'bird', 'metal', 0),
    'xu': Branch('xu', 'dog', 'earth', 1),
    'hai': Branch('hai', 'pig', 'water', 0)
}

@define
class BaZiDate():
    solar_date: datetime
    lunar_date: LunarDate
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar

    @classmethod
    def from_datetime(cls, dt):
        # convert to lunar calendar for reference
        ldate = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
        cycle_loc = dt.year % 60

        # year init
        ys_loc = (cycle_loc % 10) - 1
        ystem = _stem_lookup[list(_stem_lookup)[ys_loc]]
        yb_loc = (cycle_loc % 12) - 1
        ybranch = _branch_lookup[list(_branch_lookup)[yb_loc]]
        ypillar = Pillar(ystem, ybranch)
        
        # month init
        ms_loc = (cycle_loc % 5) * 2
        mstem = _stem_lookup[list(_stem_lookup)[ms_loc]]
        mbranch = _branch_lookup[list(_branch_lookup)[ldate.month + 1]]
        mpillar = Pillar(mstem, mbranch)

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
        dpillar = Pillar(dstem, dbranch)

        # hour init
        hs_diff = dt.hour + 1 // 2 if dt.hour < 23 else 0
        hs_start = (list(_stem_lookup).index(dpillar.stem.name) % 5) * 2
        hstem = _stem_lookup[list(_stem_lookup)[hs_start + hs_diff]]
        hbranch = _branch_lookup[list(_branch_lookup)[hs_diff]]
        hpillar = Pillar(hstem, hbranch)

        return cls(dt, ldate, ypillar, mpillar, dpillar, hpillar)
