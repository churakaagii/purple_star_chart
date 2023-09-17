from attrs import define

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
