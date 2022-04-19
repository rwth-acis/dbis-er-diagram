from enum import Enum
class NodeType(Enum):
    NOT_SPECIFIED = -1
    NODE = 1
    ATTRIBUTE = 2
    RELATION = 3
    IS_A = 4
    COMPOSED_ATTRIBUTE = 5

    def __str__(self):
        return str(self.name)