
class Target:
    def __init__(self, class_type='', label='', coordinates=[]):
        self.class_type = class_type
        self.label = label
        self.coordinates = coordinates

    def stringify(self):
        return 'Class: %s \tLabel: %s\tCoords: (%.2f, %.2f, %.2f)' % \
            ((self.class_type,)+(self.label,)+self.coordinates)

    def __str__(self):
        return self.stringify()

    def __repr__(self):
        return self.__str__()