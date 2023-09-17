'''Class for holding BaZi related informaton.
You can initialize it using only a date from the Gregorian calendar if you use
the BaZiDate.from_datetime() method.'''

from lunardate import LunarDate
from attrs import define
from datetime import datetime, date
from src.purple_star_chart import _stem_lookup, _branch_lookup, _Pillar

@define
class BaZiDate():
    solar_date: datetime
    lunar_date: LunarDate
    year_pillar: _Pillar
    month_pillar: _Pillar
    day_pillar: _Pillar
    hour_pillar: _Pillar

    @classmethod
    def from_solar_date(cls, dt):
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
