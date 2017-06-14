# -*- coding: utf-8 -*-
import types
import logging

logger = logging.getLogger('django')


class Context(object):
    """ 上下文管理器，管理变量与生成器，分别存在variables和generators两个列表里。
        bind_variable用来绑定一个变量，bind_variables用来绑定一组变量
        add_generator可以添加一个生成器
        bind_generator_next可以绑定生成器的值到一个变量，并返回当前变量值
        get_value返回一个变量的值，get_values返回所有变量
        get_generator返回一个生成器，get_generators返回所有生成器

        mod_count用来记录Context里的变量值被修改的次数（可能是重新赋值，可能是读取下个生成器值）
        """

    variables = dict()  # Maps variable name to current value
    generators = dict()  # Maps generator name to generator function
    mod_count = 0  # Lets us see if something has been altered, avoiding needless retemplating

    def bind_variable(self, variable_name, variable_value):
        """ 绑定一个变量名到value上，即赋值，可在test中使用该变量 """
        str_name = str(variable_name)
        prev = self.variables.get(str_name)
        if prev != variable_value:
            self.variables[str_name] = variable_value
            self.mod_count += 1
            logger.debug('Context: altered variable named {0} to value {1}'.format(str_name, variable_value))

    def bind_variables(self, variable_map):
        """绑定一组变量"""
        for key, value in variable_map.items():
            self.bind_variable(key, value)

    def add_generator(self, generator_name, generator):
        """ 添加一个生成器到Context，你可以通过bing_generator_next来给变量赋值。 """

        if not isinstance(generator, types.GeneratorType):
            raise ValueError('Cannot add generator named {0}, it is not a generator type'.format(generator_name))

        self.generators[str(generator_name)] = generator
        logger.debug('Context: Added generator named {0}'.format(generator_name))

    def bind_generator_next(self, variable_name, generator_name):
        """ 返回当前变量的生成器值，绑定下一个值到变量。 """
        str_gen_name = str(generator_name)
        str_name = str(variable_name)
        val = next(self.generators[str_gen_name])

        prev = self.variables.get(str_name)
        if prev != val:
            self.variables[str_name] = val
            self.mod_count += 1
            logger.debug('Context: Set variable named {0} to next value {1} from generator named {2}'.format(variable_name, val, generator_name))
        return val

    def get_values(self):
        return self.variables

    def get_value(self, variable_name):
        """ Get bound variable value, or return none if not set """
        return self.variables.get(str(variable_name))

    def get_generators(self):
        return self.generators

    def get_generator(self, generator_name):
        return self.generators.get(str(generator_name))

    def __init__(self):
        self.variables = dict()
        self.generators = dict()
