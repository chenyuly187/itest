# -*- coding: utf-8 -*-
class Context(object):

    def bind_variable(self, variable_name, variable_value):
        """ 绑定一个变量名到value上，即赋值，可在test中使用该变量 """
        str_name = str(variable_name)
        prev = self.variables.get(str_name)
        if prev != variable_value:
            self.variables[str_name] = variable_value

    def bind_variables(self, variable_map):
        """绑定一组变量"""
        for key, value in variable_map.items():
            self.bind_variable(key, value)

    def get_values(self):
        return self.variables

    def get_value(self, variable_name):
        """ Get bound variable value, or return none if not set """
        return self.variables.get(str(variable_name))

    def __init__(self):
        self.variables = dict()

# if __name__ == '__main__':
#     c = Context()
#     c.bind_variables({"val1": "i have a dog", "val2": "i have a cat"})
#     c.bind_variable("val3", "i have a pig")
#
#     print(c.get_values())
