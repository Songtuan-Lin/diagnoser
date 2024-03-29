from . import pddl_types

class Function(object):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
    @classmethod
    def parse(cls, alist, type_name):
        name = alist[0]
        arguments = pddl_types.parse_typed_list(alist[1:],
                                                default_type="number")
        return cls(name, arguments)
        
    def __str__(self):
        result = "%s(%s)" % (self.name, ", ".join(map(str, self.arguments)))
        if self.type:
            result += ": %s" % self.type
        return result

    def pddl(self):
        if len(self.arguments) == 0:
            return "({0}) - {1}".format(self.name, "number")
        return "({0} {1}) - {2}".format(self.name, ' - '.join(x.pddl() for x in self.arguments), "number")
