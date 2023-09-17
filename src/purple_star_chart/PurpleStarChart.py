#TODO redo lookup charts by enumeration

from attrs import define, field
from datetime import datetime
from .BaZiDate import BaZiDate
from src.purple_star_chart import _Stem, _Branch, _stem_lookup, _branch_lookup
from lunardate import LunarDate

@define
class PSPalace:
    '''object that contains data for a single palace'''
    palace_name: str
    stem: _Stem
    branch: _Branch
    stars: list = field(factory=list)
    is_bodypalace: bool = field(init=False, default=False)

@define
class PSPalaces:
    '''object for holding palace information for an entire chart
    Currently just a fancy dict, but prepping for future development and for
    more intuitive attribute handling'''
    life: PSPalace
    siblings: PSPalace
    spouse: PSPalace
    children: PSPalace
    wealth: PSPalace
    health: PSPalace
    travel: PSPalace
    friends: PSPalace
    career: PSPalace
    property: PSPalace
    fortune: PSPalace
    parents: PSPalace
    zi: PSPalace
    chou: PSPalace
    yin: PSPalace
    mao: PSPalace
    chen: PSPalace
    si: PSPalace
    wu: PSPalace
    wei: PSPalace
    shen: PSPalace
    you: PSPalace
    xu: PSPalace
    hai: PSPalace
    ziwei: PSPalace = field(init=False, default=None)

@define
class PurpleStarChart:
    '''top level object for a purple star chart'''
    solar_date: datetime
    lunar_date: LunarDate
    bazi_info: BaZiDate
    palaces: PSPalaces
    elemental_phase: str = field(init=False, default=None)

    @classmethod
    def initialize_chart(cls, solar_dt):
        '''set up an empty chart based on date from gregorian calendar'''
        ldate = LunarDate.fromSolarDate(solar_dt.year, solar_dt.month, solar_dt.day)
        bazi = BaZiDate.from_solar_date(solar_dt)
        stems = list(_stem_lookup)
        branches = list(_branch_lookup)

        # reorder branches from yin, reorder stems for matching based on year stem
        palace_branch_order = branches[2:len(branches)] + ['zi', 'chou']
        palace_stem_start = ((stems.index(bazi.year_pillar.stem.name) % 5) * 2 + 2) % 10
        palace_stem_order = stems[palace_stem_start:len(stems)] + stems[0:palace_stem_start]
        palace_stem_for_zip = palace_stem_order + palace_stem_order[0:2]
        stem_branch_zip = zip(palace_stem_for_zip, palace_branch_order, strict=True)
        palace_pillars = {branch: (_stem_lookup[stem], _branch_lookup[branch]) for stem, branch in stem_branch_zip}

        # for life palace, start at lunar month and step backwards based on branch ordering from zi, -1 for off by one
        hour_branch_loc = branches.index(bazi.hour_pillar.branch.name)
        lp_branch_loc = ldate.month - hour_branch_loc - 1

        # set body pillar similar to life pillar
        bp_branch_loc = (ldate.month + hour_branch_loc - 1) % 12
        bp_branch_name = palace_branch_order[bp_branch_loc]

        # generate pillars for all palaces based on life palace location and reordered branches/stems
        palaces_dict = dict()
        palace_names = ['life', 'siblings', 'spouse', 'children', 'wealth', 'health', 'travel', 'friends', 'career', 'property', 'fortune', 'parents']
        for palace in palace_names:
            distance = palace_names.index(palace)
            lookup_name = palace_branch_order[(lp_branch_loc + distance) % 12]
            this_stem, this_branch = palace_pillars[lookup_name]
            this_palace = PSPalace(palace, this_stem, this_branch)
            if bp_branch_name == lookup_name:
                this_palace.is_bodypalace = True
            palaces_dict[palace] = this_palace
            palaces_dict[lookup_name] = palaces_dict[palace]

        # generate class
        palaces = PSPalaces(**palaces_dict)
        return cls(solar_dt, ldate, bazi, palaces)
    
    def _derive_elemental_phase(self):
        stems = list(_stem_lookup)
        branches = list(_branch_lookup)
        phases = [
            [2, 6, 3, 5, 4, 6],
            [6, 5, 4, 3, 2, 5],
            [5, 3, 2, 4, 6, 3],
            [3, 4, 6, 2, 5, 4],
            [4, 2, 5, 6, 3, 2]
        ]
        str_lookup = {
            2: 'water',
            3: 'wood',
            4: 'metal',
            5: 'earth',
            6: 'fire'
        }

        stem_ploc = stems.index(self.bazi_info.year_pillar.stem.name) % 5
        lp_branch_ploc = branches.index(self.palaces.life.branch.name) // 2
        self.elemental_phase = str_lookup[phases[stem_ploc][lp_branch_ploc]]

    def _place_ziwei(self):
        branches = list(_branch_lookup)
        ziwei_lookup = {
            'water': [1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11,
                0, 0, 1, 1, 2, 2, 3, 3, 4],
            'wood': [4, 1, 2, 5, 2, 3, 6, 3, 4, 7, 4, 5, 8, 5, 6, 9, 6, 7, 10, 7, 8,
                11, 8, 9, 0, 9, 10, 1, 10, 11],
            'metal': [11, 4, 1, 2, 0, 5, 2, 3, 1, 6, 3, 4, 2, 7, 4, 5, 3, 8, 5, 6, 4,
                9, 6, 7, 5, 10, 7, 8, 6, 11],
            'earth': [6, 11, 4, 1, 2, 7, 0, 5, 2, 3, 8, 1, 6, 3, 4, 9, 2, 7, 4, 5, 10,
                3, 8, 5, 6, 11, 4, 9, 6, 7],
            'fire': [9, 6, 11, 4, 1, 2, 10, 7, 0, 5, 2, 3, 11, 8, 1, 6, 3, 4, 0, 9, 2,
                7, 4, 5, 1, 10, 3, 8, 5, 7]
        }

        ziwei_loc = branches[ziwei_lookup[self.elemental_phase][self.lunar_date.day -1]]
        ziwei_palace = getattr(self.palaces, ziwei_loc)
        ziwei_palace.stars.append('ziwei')
        self.palaces.ziwei = ziwei_palace
    
    def add_stars(self):
        # stems = list(_stem_lookup)
        # branches = list(_branch_lookup)

        self._derive_elemental_phase
        self._place_ziwei
