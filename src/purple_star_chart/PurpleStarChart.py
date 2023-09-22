#TODO redo lookup charts by enumeration

from attrs import define, field
from datetime import datetime
from .BaZiChart import BaZiChart
from src.purple_star_chart import _stem_lookup, _branch_lookup, _stems, _branches
from src.purple_star_chart.constructor_classes import Pillar, PSPalace, PSPalaces
from lunardate import LunarDate

@define
class PurpleStarChart:
    '''top level object for a purple star chart'''
    solar_date: datetime
    lunar_date: LunarDate
    bazi: BaZiChart
    palaces: PSPalaces
    _hour_offset: int
    _palace_by_branch: dict = field(factory=dict)
    elemental_phase: str = field(init=False, default=None)
    _palace_by_star: dict = field(factory=dict)

    @classmethod
    def initialize_chart(cls, solar_dt):
        '''set up an empty chart based on date from gregorian calendar
        requires python datetime.date or datetime.datetime format'''
        ldate = LunarDate.fromSolarDate(solar_dt.year, solar_dt.month, solar_dt.day)
        this_bazi = BaZiChart.from_solar_date(solar_dt)

        # reorder branches from yin, reorder stems for matching based on year stem
        palace_branch_order = _branches[2:len(_branches)] + ['zi', 'chou']
        palace_stem_start = ((_stems.index(this_bazi.year.stem.name) % 5) * 2 + 2) % 10
        palace_stem_order = _stems[palace_stem_start:len(_stems)] + _stems[0:palace_stem_start]
        palace_stem_for_zip = palace_stem_order + palace_stem_order[0:2]
        stem_branch_zip = zip(palace_stem_for_zip, palace_branch_order, strict=True)
        palace_pillars = {branch: (_stem_lookup[stem], _branch_lookup[branch]) for stem, branch in stem_branch_zip}

        # for life palace, start at lunar month and step backwards based on branch ordering from zi, -1 for off by one
        hour_branch_loc = _branches.index(this_bazi.hour.branch.name)
        lp_branch_loc = ldate.month - hour_branch_loc - 1

        # set body pillar similar to life pillar
        bp_branch_loc = (ldate.month + hour_branch_loc - 1) % 12
        bp_branch_name = palace_branch_order[bp_branch_loc]

        # generate pillars for all palaces based on life palace location and reordered branches/stems
        palaces_dict = dict()
        palaces_bybranch = dict()
        palace_names = ['life', 'siblings', 'spouse', 'children', 'wealth', 'health', 'travel', 'friends', 'career', 'property', 'fortune', 'parents']
        for palace in palace_names:
            distance = palace_names.index(palace)
            lookup_name = palace_branch_order[(lp_branch_loc + distance) % 12]
            this_stem, this_branch = palace_pillars[lookup_name]
            this_pillar = Pillar(palace, this_stem, this_branch)
            this_palace = PSPalace(palace, this_pillar)
            if bp_branch_name == lookup_name:
                this_palace.is_bodypalace = True
            palaces_dict[palace] = this_palace
            palaces_bybranch[lookup_name] = this_palace

        # generate class
        palaces = PSPalaces(**palaces_dict)
        return cls(solar_dt, ldate, this_bazi, palaces, hour_branch_loc, palaces_bybranch)

    def _add_star_by_branch(self, star_name, start_loc, offset=0, back=False):
        '''private helper that traverses branches based on parameters
        and updates palace at final branch with star_name'''
        from operator import neg

        this_loc = _branches.index(start_loc) if isinstance(start_loc, str) else start_loc
        offset = neg(offset) if back == True else offset
        this_branch = _branches[(this_loc + offset) % 12]
        palace = self._palace_by_branch[this_branch]
        palace.stars.append(star_name)
        self._palace_by_star[star_name] = palace.name

    def _apply_branch_traversal(self, starmaps, backstars=[], **kwargs):
        for star, loc in starmaps.items():
            isBack = True if star in backstars else False
            self._add_star_by_branch(star, loc, back=isBack, **kwargs)
    
    def _derive_elemental_phase(self):
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

        stem_ploc = _stems.index(self.bazi.year.stem.name) % 5
        lp_branch_ploc = _branches.index(self.palaces.life.pillar.branch.name) // 2
        self.elemental_phase = str_lookup[phases[stem_ploc][lp_branch_ploc]]

    def _plot_ziwei(self):
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

        ziwei_loc = _branches[ziwei_lookup[self.elemental_phase][self.lunar_date.day -1]]
        ziwei_palace = self._palace_by_branch[ziwei_loc]
        ziwei_palace.stars.append('zi_wei')
        self._palace_by_star['zi_wei'] = ziwei_palace

    def _plot_major_stars(self):
        '''updates palaces with 14 major stars'''
        # locations of 14 major stars if ziwei is at zi
        startlocs = {
            'tian_ji': 11,
            'tai_yang': 9,
            'wu_qu': 8,
            'tian_tong': 7,
            'lian_zhen': 4
        }
        startlocs_back = {
            'tian_fu': 4,
            'tai_yin': 5,
            'tan_lang': 6,
            'ju_men': 7,
            'tian_xiang': 8,
            'tian_liang': 9,
            'qi_sha': 10,
            'po_jun': 2
        }
        backlist = list(startlocs_back)
        startlocs.update(startlocs_back)

        # get chart's ziwei location branch index
        zwpalace = self._palace_by_star['zi_wei']
        zwloc = _branches.index(zwpalace.pillar.branch.name)

        # traverse branches to get final star locations
        self._apply_branch_traversal(startlocs, backstars=backlist, offset=zwloc)

    def _plot_hour_stars(self):
        '''updates palaces with stars requiring birth hour to derive'''
        startlocs = {
            'wen_chang': 10,
            'wen_qu': 4,
            'di_jie': 11,
            'di_kong': 11,
            'tai_fu': 6,
            'feng_gao': 2,
            'ling_xing': 10
        }
        backstars = ['wen_chang', 'di_kong']

        # get branch group based on year pillar branch
        yr_branch = self.bazi.year.branch.name
        yr_grp = _branches.index(yr_branch) % 4

        # update start locations for huo xing and maybe ling xing based on group
        if yr_grp == 0:
            startlocs.update({'huo_xing': 2})
        elif yr_grp == 1:
            startlocs.update({'huo_xing': 3})
        elif yr_grp == 2:
            startlocs.update({'huo_xing': 1, 'ling_xing': 3})
        elif yr_grp == 3:
            startlocs.update({'huo_xing': 9})

        self._apply_branch_traversal(startlocs, backstars=backstars, offset=self._hour_offset)

    def _plot_month_stars(self):
        lmonth = self.lunar_date.month
        startlocs = {
            'zuo_fu': 3,
            'you_bi': 11,
            'tian_xing': 8,
            'tian yao': 0
        }
        backstars = ['you_bi']

        self._apply_branch_traversal(startlocs, backstars=backstars, offset=lmonth)

        yuema_list = ['hai', 'shen', 'si', 'yin']
        yuema_br = yuema_list[lmonth % 4]
        self._add_star_by_branch('yue_ma', yuema_br)

        jieshen_list = ['shen', 'xu', 'zi', 'yin', 'chen', 'wu']
        jieshen_br = jieshen_list[(lmonth - 1) // 2]
        self._add_star_by_branch('jie_shen', jieshen_br)

        tianwu_list = ['hai', 'si', 'shen', 'yin']
        tianwu_br = tianwu_list[lmonth % 4]
        self._add_star_by_branch('tian_wu', tianwu_br)

        tianyue_list = ['xu', 'si', 'chen', 'yin', 'wei', 'mao', 'hai', 'wei', 
                        'yin', 'wu', 'xu', 'yin']
        tianyue_br = tianyue_list[lmonth - 1]
        self._add_star_by_branch('tian_yue', tianyue_br)

        # TODO this can be done with clever math
        yinsha_list = ['chen', 'yin', 'zi', 'xu', 'shen', 'wu']
        yinsha_br = yinsha_list[lmonth % 6]
        self._add_star_by_branch('yin_sha', yinsha_br)

    def _plot_day_stars(self):
        def _get_branch_from_star(star):
            palace = self._palace_by_star[star]
            return palace.pillar.branch.name
        
        lday = self.lunar_date.day

        self._add_star_by_branch('san_tai', _get_branch_from_star('zuo_fu'), 
                                 offset=lday)
        self._add_star_by_branch('ba_zuo', _get_branch_from_star('you_bi'), 
                                 offset=lday, back=True)
        self._add_star_by_branch('en_guang', _get_branch_from_star('wen_chang'),
                                 offset=(lday - 1))
        self._add_star_by_branch('tian_gui', _get_branch_from_star('wen_qu'),
                                 offset=(lday - 1))

    def add_stars(self):
        self._derive_elemental_phase()
        self._plot_ziwei()
        self._plot_major_stars()
        self._plot_hour_stars()
        self._plot_month_stars()
        self._plot_day_stars()
