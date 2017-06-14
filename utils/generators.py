# -*- coding: utf-8 -*-
"""
    generator_basic_ids         id生成器
    generator_random_int32      随机数字生成器（最大32位有符号数）
    generator_fixed_sequence    固定序列生成器（传入字典，从 values 中循环读取）
    generator_choice            随机选择生成器（传入字典，从 values 中随机选择）
    generator_random_text       通过给定的字符，生成随机文本的生成器
                                    传入格式 {'character_set': 'letters', 'min_length': 4, 'max_length': 10}
                                    或者    {‘characters': '123456zxcv', 'length': 8}
                                    可指定字符集合或自定义，可指定最长最短长度或定长

    factory_generate_ids        id生成器工厂，能指定起始值以及步长，返回生成器函数
    factory_generate_text       文本生成器工厂，能指定字符集，最小长度以及最大长度，返回生成器函数
    factory_fixed_sequence      固定序列生成器工厂，传入list，返回生成器函数
    factory_choice              随机选择生成器工厂，传入list，返回生成器函数

    register_generator          注册生成器类型以及对应方法到 GENERATOR_TYPES 以及 GENERATOR_PARSING 中

    **parse_generator           解析方法，传入字典，得到生成器
                                    传入的 type 参数需要在 GENERATOR_TYPES 以及 GENERATOR_PARSING 注册过
                                    其他传入相应参数
                                    如：
                                    {'type': 'number_sequence', 'start': 10, 'increment': 5}
                                    {'type': 'random_int'}
                                    {'type': 'fixed_sequence', 'values': ['a', 'b', 'c', 'd']}
                                    {'type': 'random_text', 'character_sets': 'ascii_letters', 'length': 10}
"""
import random
import string
from parsing import lowercase_keys


INT32_MAX_VALUE = 2147483647  # Max of 32 bit unsigned int

# Character sets to use in text generation, python string plus extras
CHARACTER_SETS = {
    'ascii_letters': string.ascii_letters,
    'ascii_lowercase': string.ascii_lowercase,
    'ascii_uppercase': string.ascii_uppercase,
    'digits': string.digits,
    'hexdigits': string.hexdigits,
    'hex_lower':  string.digits + 'abcdef',
    'hex_upper':  string.digits + 'ABCDEF',
    'letters': string.ascii_letters,
    'lowercase': string.ascii_lowercase,
    'octdigits': string.octdigits,
    'punctuation': string.punctuation,
    'printable': string.printable,
    'uppercase': string.ascii_uppercase,
    'whitespace': string.whitespace,
    'url.slug': string.ascii_lowercase + string.digits + '-',
    'url.safe': string.ascii_letters + string.digits + '-~_.',
    'alphanumeric': string.ascii_letters + string.digits,
    'alphanumeric_lower': string.ascii_lowercase + string.digits,
    'alphanumeric_upper': string.ascii_uppercase + string.digits
}


def factory_generate_ids(starting_id=1, increment=1):
    """ Return function generator for ids starting at starting_id
        Note: needs to be called with () to make generator """
    def generate_started_ids():
        val = starting_id
        local_increment = increment
        while True:
            yield val
            val += local_increment
    return generate_started_ids


def generator_basic_ids():
    """ 返回id生成器，以1开始 """
    return factory_generate_ids(1)()


def generator_random_int32():
    """ 有符号整数生成器（最高32位） """
    rand = random.Random()
    while True:
        yield random.randint(0, INT32_MAX_VALUE)


def factory_generate_text(legal_characters=string.ascii_letters, min_length=8, max_length=8):
    """ Returns a generator function for text with given legal_characters string and length
        Default is ascii letters, length 8

        For hex digits, combine with string.hexstring, etc
        """
    def generate_text():
        local_min_len = min_length
        local_max_len = max_length
        rand = random.Random()
        while True:
            length = random.randint(local_min_len, local_max_len)
            array = [random.choice(legal_characters) for x in xrange(0, length)]
            yield ''.join(array)

    return generate_text


def factory_fixed_sequence(values):
    """ Return a generator that runs through a list of values in order, looping after end """
    def seq_generator():
        my_list = list(values)
        i = 0
        while True:
            yield my_list[i]
            i += 1
            if i == len(my_list):
                i = 0
    return seq_generator


def generator_fixed_sequence(config):
    """ Parse fixed sequence string """
    val = config.get('values')
    if not val:
        raise ValueError('Values for fixed sequence must exist')
    if not isinstance(val, list):
        raise ValueError('Values must be a list of entries')
    return factory_fixed_sequence(val)()


def factory_choice(values):
    """ Return a generator that picks values from a list randomly """
    def choice_generator():
        my_list = list(values)
        rand = random.Random()
        while True:
            yield random.choice(my_list)
    return choice_generator


def generator_choice(config):
    """ Parse choice generator """
    val = config.get('values')
    if not val:
        raise ValueError('Values for choice sequence must exist')
    if not isinstance(val, list):
        raise ValueError('Values must be a list of entries')
    return factory_choice(val)()


def generator_random_text(config):
    """ Parses configuration options for a random text generator """
    character_set = config.get(u'character_set')
    characters = None
    if character_set:
        character_set = character_set.lower()
        if character_set not in CHARACTER_SETS:
            raise ValueError(
                "Illegal character set name, is not defined: {0}".format(character_set))
        characters = CHARACTER_SETS[character_set]
    else:  # Custom characters listing, not a character set
        characters = str(config.get(u'characters'))

    min_length = 8
    max_length = 8

    if config.get(u'min_length'):
        min_length = int(config.get(u'min_length'))
    if config.get(u'max_length'):
        max_length = int(config.get(u'max_length'))

    if config.get(u'length'):
        length = int(config.get(u'length'))
        min_length = length
        max_length = length

    if characters:
        return factory_generate_text(legal_characters=characters, min_length=min_length, max_length=max_length)()
    else:
        return factory_generate_text(min_length=min_length, max_length=max_length)()


# List of valid generator types
GENERATOR_TYPES = {
    'number_sequence',
    'random_int',
    'random_text',
    'fixed_sequence',
    'choice'
}

GENERATOR_PARSING = {
    'fixed_sequence': generator_fixed_sequence,
    'choice': generator_choice,
}


def register_generator(typename, parse_function):
    """ 注册生成器，把生成器类型和解析方法传入到，添加到 GENERATOR_TYPES 和 GENERATOR_PARSING 中 """
    if not isinstance(typename, basestring):
        raise TypeError(
            'Generator type name {0} is invalid, must be a string'.format(typename))
    if typename in GENERATOR_TYPES:
        raise ValueError(
            'Generator type named {0} already exists'.format(typename))
    GENERATOR_TYPES.add(typename)
    GENERATOR_PARSING[typename] = parse_function


def parse_generator(configuration):
    configuration = lowercase_keys(configuration)
    gen_type = str(configuration.get(u'type')).lower()

    if gen_type not in GENERATOR_TYPES:
        raise ValueError(
            'Generator type given {0} is not valid '.format(gen_type))

    # Do the easy parsing, delegate more complex logic to parsing functions
    if gen_type == u'number_sequence':
        start = configuration.get('start')
        increment = configuration.get('increment')
        if not start:
            start = 1
        else:
            start = int(start)
        if not increment:
            increment = 1
        else:
            increment = int(increment)
        return factory_generate_ids(start, increment)()
    elif gen_type == u'random_int':
        return generator_random_int32()
    elif gen_type == u'random_text':
        return generator_random_text(configuration)
    elif gen_type in GENERATOR_TYPES:
        return GENERATOR_PARSING[gen_type](configuration)
    else:
        raise Exception("Unknown generator type: {0}".format('gen_type'))
