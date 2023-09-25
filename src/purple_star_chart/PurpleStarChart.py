#TODO redo lookup charts by enumeration

from attrs import define, field
from datetime import datetime
from .BaZiChart import BaZiChart
from src.purple_star_chart import _stem_lookup, _branch_lookup, _stems, _branches
from src.purple_star_chart.constructor_classes import Pillar, PSPalace, PSPalaces, Star
from lunardate import LunarDate

@define
class PurpleStarChart:
    '''top level object for a purple star chart'''
    solar_date: datetime
    lunar_date: LunarDate
    bazi: BaZiChart
    palaces: PSPalaces
    gender: str
    _hour_offset: int
    _palace_by_branch: dict
    _traverse_back: bool
    elemental_phase: str
    _palace_by_star: dict = field(factory=dict)

    @classmethod
    def initialize_chart(cls, solar_dt, gender):
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

        # determine traversal direction based on gender and polarity
        isYang = this_bazi.year.stem.polarity
        if (gender == 'male' and isYang) or (gender == 'female' and not isYang):
            goback = False
        elif (gender == 'male' and not isYang) or (gender == 'female' and isYang):
            goback = True

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
                palaces_dict['body'] = this_palace
            palaces_dict[palace] = this_palace
            palaces_bybranch[lookup_name] = this_palace
        palaces = PSPalaces(**palaces_dict)

        # derive elemental phase
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
        stem_ploc = _stems.index(this_bazi.year.stem.name) % 5
        lp_branch_ploc = _branches.index(palaces.life.pillar.branch.name) // 2
        phase = str_lookup[phases[stem_ploc][lp_branch_ploc]]

        # generate class
        return cls(solar_dt, ldate, this_bazi, palaces, gender, hour_branch_loc, palaces_bybranch, goback, phase)

    def _add_star_by_branch(self, star_name, start_loc, offset=0, back=False):
        '''private helper that traverses branches based on parameters
        and updates palace at final branch with star_name'''
        from operator import neg

        this_loc = _branches.index(start_loc) if isinstance(start_loc, str) else start_loc
        offset = neg(offset) if back == True else offset
        this_branch = _branches[(this_loc + offset) % 12]
        palace = self._palace_by_branch[this_branch]
        palace.stars.append(Star(star_name))
        self._palace_by_star[star_name] = palace

    def _add_star_by_palace(self, star, palace):
        this_pal = getattr(self.palaces, palace) if isinstance(palace, str) else palace
        this_pal.stars.append(Star(star))
        self._palace_by_star[star] = this_pal

    def _apply_branch_traversal(self, starmaps, backstars=[], **kwargs):
        for star, loc in starmaps.items():
            isBack = True if star in backstars else False
            self._add_star_by_branch(star, loc, back=isBack, **kwargs)

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
        self._add_star_by_palace('zi_wei', self._palace_by_branch[ziwei_loc])

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

    def _get_branch_from_star(self, star):
        palace = self._palace_by_star[star]
        return palace.pillar.branch.name
    
    def _plot_day_stars(self):
        starts = {
            'san_tai': ('zuo_fu', 0),
            'ba_zuo': ('you_bi', 0),
            'en_guang': ('wen_chang', -1),
            'tian_gui': ('wen_qu', -1)
        }

        for star, params in starts.items():
            this_br = self._get_branch_from_star(params[0])
            offset = self.lunar_date.day + params[1] - 1
            back = True if star == 'ba_zuo' else False
            self._add_star_by_branch(star, this_br, offset=offset, back=back)

    def _plot_year_stars(self):
        ystem_loc = _stems.index(self.bazi.year.stem.name)
        ystem_maps = {
            'lu_cun': ['yin', 'mao', 'si', 'wu', 'si', 'wu', 'shen', 'you', 
                       'hai', 'zi'],
            'qing_yang': ['mao', 'chen', 'wu', 'wei', 'wu', 'wei', 'you', 'xu', 
                          'zi', 'chou'],
            'tuo_luo': ['chou', 'yin', 'chen', 'si', 'chen', 'si', 'wei', 
                        'shen', 'xu', 'hai'],
            'tian_yue': ['chou', 'zi', 'hai', 'hai', 'chou', 'zi', 'chou', 
                         'wu', 'mao','mao'],
            'tian_kui': ['wei', 'shen', 'you', 'you','wei', 'shen', 'wei', 
                         'yin', 'si', 'si'],
            'tian_gong': ['wei', 'chen', 'si', 'yin', 'mao', 'you', 'hai', 
                          'you', 'xu', 'wu'],
            'tian_fu': ['you', 'shen', 'zi', 'hai', 'mao', 'yin', 'wu', 'si', 
                        'wu', 'si']
        }
        trans_maps = {
            'hua_lu': ['lian_zhen', 'tian_ji', 'tian_tong', 'tai_yin', 'tan_lang', 
                       'wu_qu', 'tai_yang', 'ju_men', 'tian_liang', 'po_jun'],
            'hua_quan': ['po_jun', 'tian_liang', 'tian_ji', 'tian_tong', 'tai_yin', 
                         'tan_lang', 'wu_qu', 'tai_yang', 'zi_wei', 'ju_men'],
            'hua_ke': ['wu_qu', 'zi_wei', 'wen_chang', 'tian_ji', 'you_bi', 
                       'tian_liang', 'tai_yin', 'wen_qu', 'zuo_fu', 'tai_yin'],
            'hua_ji': ['tai_yang', 'tai_yin', 'lian_zhen', 'ju_men', 'tian_ji', 
                       'wen_qu', 'tian_tong', 'wen_chang', 'wu_qu', 'tan_lang']
        }

        for star, loc_list in ystem_maps.items():
            self._add_star_by_branch(star, loc_list[ystem_loc])

        for star, loc_list in trans_maps.items():
            this_br = self._get_branch_from_star(loc_list[ystem_loc])
            self._add_star_by_branch(star, this_br)

    def _regen_branches_from(self, start, back_check=True):
        ind = _branches.index(start) if isinstance(start, str) else start
        regen = _branches[ind:] + _branches[0:ind]
        if back_check and self._traverse_back:
            cut = regen[1:]
            cut.reverse()
            out = [regen[0]] + cut
        else:
            out = regen
        return out

    def _plot_boshi(self):
        '''plots Bo Shi stars
        assumes that user has set gender after initializing chart but before 
        calling this'''
        boshi = ['bo_shi', 'li_shi', 'qing_long', 'xiao_hao', 'jiang_jun', 
                 'zou_shu', 'fei_lian', 'xi_shen', 'bing_fu', 'da hao', 
                 'fu_bing', 'guan_fu']

        boshi_branches = self._regen_branches_from(self._get_branch_from_star('lu_cun'))

        for star, branch in zip(boshi, boshi_branches):
            self._add_star_by_branch(star, branch)

    def _plot_yearbr_stars(self):
        this_maps = {
            'tian_ku': 6,
            'tian_xu': 6,
            'long_chi': 4,
            'feng_ge': 10,
            'hong_luan': 3,
            'tian_xi': 9,
            'tian_kong': 1,
            'tai_sui': 0
        }
        backstars = ['tian_ku', 'feng_ge', 'hong_luan', 'tian_xi']
        ybr_ind = _branches.index(self.bazi.year.branch.name)
        self._apply_branch_traversal(this_maps, backstars, offset=ybr_ind)

        # gu chen, gua su
        this_ind = ((ybr_ind + 1) % 12) // 3
        quad_maps = {
            'gu_chen': ['yin', 'si', 'shen', 'hai'],
            'gua_su': ['xu', 'chou', 'chen', 'wei']
        }
        for star, amap in quad_maps.items():
            this_br = amap[this_ind]
            self._add_star_by_branch(star, this_br)

        # fei lian
        this_map = [_branches[8:11], _branches[5:8], _branches[2:5], _branches[-1:2]]
        selector = ybr_ind // 3
        mod3_ind = ybr_ind % 3
        this_br = this_map[selector][mod3_ind]
        self._add_star_by_branch('fei_lian', this_br)

        # po sui
        this_map = ['si', 'chou', 'you']
        this_br = this_map[mod3_ind]
        self._add_star_by_branch('po_sui', this_br)

        # tian cai
        this_map = ['life', 'parents', 'fortune', 'property', 'career', 'friends', 
                    'travel', 'health', 'wealth', 'children', 'spouse', 'siblings']
        pal_name = this_map[ybr_ind]
        self._add_star_by_palace('tian_cai', pal_name)

        # tian shou((ybr // 2) * 2) + 2
        self._add_star_by_branch('tian_shou', self.palaces.body.pillar.branch.name, offset=ybr_ind)

        # tian ma
        this_map = {
            'tian_ma': ['yin', 'hai', 'shen', 'si'],
            'hua_gai': ['chen', 'chou', 'xu','wei'],
            'xian_chi': ['you', 'wu', 'mao', 'zi']
        }
        mod4_ind = ybr_ind % 4
        for star, amap in this_map.items():
            this_br = amap[mod4_ind]
            self._add_star_by_branch(star, this_br)

    def _plot_changshen(self):
        changshen = ['chang_shen', 'mu_yu', 'guan_dai', 'lin_guan', 'di_wang', 
                     'shuai', 'bing', 'si', 'mu', 'jue', 'tai', 'yang']
        start_by_el = {
            'water': 'shen',
            'wood': 'hai',
            'metal': 'si',
            'earth': 'shen',
            'fire': 'yin'
        }
        this_branches = self._regen_branches_from(start_by_el[self.elemental_phase])
        for star, branch in zip(changshen, this_branches):
            self._add_star_by_branch(star, branch)

    def _plot_misc_stars(self):
        # jie kong
        from operator import abs

        bstem = _stems.index(self.bazi.year.stem.name)
        br_ind = (abs((bstem // 2) - 4) * 2) + (bstem % 2)
        this_br = _branches[br_ind]
        self._add_star_by_branch('jie_kong', this_br)

        # xun kong
        ybr = _branches.index(self.bazi.year.branch.name)
        start = (((ybr // 2) * 2) + 2) % 12
        this_branches = self._regen_branches_from(start, back_check=False)
        yst = _stems.index(self.bazi.year.stem.name)
        this_br = this_branches[yst]
        self._add_star_by_branch('xun_kong', this_br)

        # tian shang
        self._add_star_by_palace('tian_shang', 'friends')

        # tian shi
        self._add_star_by_palace('tian_shi', 'health')

    def _get_star_obj(self, star_name):
        palace = self._palace_by_star[star_name]
        for star in palace.stars:
            if star.name == star_name:
                return star

    def _add_details_to_stars(self):
        # life master
        lm_map = ['tan_lang', 'ju_men', 'lu_cun', 'wen_qu', 'lian_zhen', 
                  'wu_qu', 'po_jun', 'wu_qu', 'lian_zhen', 'wen_qu', 'lu_cun', 
                  'ju_men']
        lm_lookup = dict(zip(_branches, lm_map))
        lm_name = lm_lookup[self.palaces.life.pillar.branch.name]
        lm_star = self._get_star_obj(lm_name)
        lm_star.isLifeMaster = True

        # body master
        bm_map = ['huo_xing', 'tian_xiang', 'tian_liang', 'tian_tong', 'wen_chang', 'tian_ji'] * 2
        bm_lookup = dict(zip(_branches, bm_map))
        bm_name = bm_lookup[self.bazi.year.branch.name]
        bm_star = self._get_star_obj(bm_name)
        bm_star.isBodyMaster = True

    def add_stars(self):
        self._plot_ziwei()
        self._plot_major_stars()
        self._plot_hour_stars()
        self._plot_month_stars()
        self._plot_day_stars()
        self._plot_year_stars()
        self._plot_boshi()
        self._plot_yearbr_stars()
        self._plot_changshen()
        self._plot_misc_stars()
        self._add_details_to_stars()
