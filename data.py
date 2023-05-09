from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Assignment:
    name: str
    date: str
    earned: Decimal
    possible: Decimal

    @property
    def score(self):
        return self.earned / self.possible
    
    def __str__(self):
        return f"{self.name} ({self.date}): {self.score:.2%}"
    
@dataclass
class Section:
    data: list[Assignment]
    name: str
    weight: Decimal


    @property
    def earned(self):
        return sum(assignment.earned for assignment in self.data)
    
    @property
    def possible(self):
        return sum(assignment.possible for assignment in self.data)
    
    @property
    def value(self):
        return (self.earned / self.possible) * self.weight
    
    # TODO: Add averageAtDay method

    # TODO: Add weightAtDay method
    
class SectionTimeline:
    ...

@dataclass
class Course:
    data: list[Section]
    name: str

    def _post_init(self):
        self.splitIntoSections()

    def splitIntoSections(self) -> None:
        outlist = []
        curSection = []

        sectWeights = {}

        for row in self.data:
            if type(row[-1]) is str:
                try:
                    sectWeights[len(sectWeights)] = Decimal(row[-1][:-2])/100, row[1]
                except ValueError:
                    pass
        del(row)


        pass
        for assignment in self.data:
            # Check valid assignment

            # EX:
            # [nan, '08/23/22', 'Verse Memory - Jeremiah 17:9', 14.0, 14.0, 'x1', '14', '100.0', nan]

            isAssignment = True
            isSection = True

            try:
                if type(assignment[8]) is str:
                    assignment[8]: str
                    if str(assignment[8]).find('%') != -1:
                        isAssignment = False
                        isSection = True
                    else:
                        raise ValueError("This is a bug.")
                else:
                    isAssignment = True
                    isSection = False
            except AttributeError:
                isAssignment = True
                isSection = False
                

            corrTypeAssignment = [[float, str], [str], [str], [float], [float], [str], [str], [str], [str, float]]
            corrTypeSection = [[str], [str], [str], [float], [float], [str], [str], [str], [str]]
            corrTypeSection = [[str], [str], [str], [float], [float], [str], [str], [str], [str]]

            for index, val in enumerate(assignment):
                if not type(val) in corrTypeAssignment[index]:
                    isAssignment = False

            
            for index, val in enumerate(assignment):
                if not type(val) in corrTypeSection[index]:
                    isSection = False


            if assignment[0] == assignment[1] == assignment[2]:
                isAssignment = False
            
            if isAssignment and isSection:
                raise ValueError("This is a bug.")


            if isAssignment:
                assignment[3] = assignment[3] if assignment[3] > 0 else 0
                curSection.append(Assignment(assignment[2],assignment[3],assignment[4], date=assignment[1]))
            elif isSection:
                outlist += [curSection]
                curSection = []
            else:
                print(f"Subsection header? {assignment}")
                pass

        outlist += [curSection]
        outlist.pop(0)

        for section in outlist:
            sect = sectWeights[outlist.index(section)]
            self.sections.append(Section(section, sect[0], sect[1]))

    @property
    def score(self):
        return sum(section.value for section in self.data) / (1 - sum(section.weight for section in self.data))

