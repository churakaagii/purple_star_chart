from attrs import define, field

@define
class Polarity():
    polarity: bool

    def polarity_str(self):
        if self.polarity == True:
            return 'yang'
        elif self.polarity == False:
            return 'yin'
        else:
            return None

@define
class Stem(Polarity):
    name: str
    element: str

@define
class Branch(Polarity):
    name: str
    animal: str
    element: str

@define
class Pillar():
    type: str
    stem: Stem
    branch: Branch

@define
class PSPalace:
    '''object that contains data for a single palace'''
    name: str
    pillar: Pillar
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
    body: PSPalace
