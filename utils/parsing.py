# -*- coding: utf-8 -*-
"""
    一些工具方法，用于解析数据

    encode_unicode_bytes        将 UNICODE 字符串进行 UTF-8 编码
    safe_substitute_unicode_template        将传入的字符串用传入的字典进行 template 解析并返回
    safe_to_json        将传入的对象安全转化成 json 字符串
    flatten_dictionaries        将传入的列表转化成字典（传入的列表需是字典的列表，不是列表则原样返回）
    lowercase_keys      将字典的所有 key 降成小写
    safe_to_bool        将输入转化成 bool
    coerce_to_string        强制转化成 UNICODE 字符串
    coerce_string_to_ascii      强制转化成 ASCII 字符串
    coerce_http_method      强制 HTTP METHOD
    coerce_list_of_ints     强制转化成一个整型的列表

"""
import string


def encode_unicode_bytes(my_string):
    """ 将 Unicode 字符串转为 UTF-8 字符串"""
    if not isinstance(my_string, basestring):
        my_string = repr(my_string)

    if isinstance(my_string, str):
        return my_string
    elif isinstance(my_string, unicode):
        return my_string.encode('utf-8')


def safe_substitute_unicode_template(templated_string, variable_map):
    """ 用 string.Template 的 safe_substitute 方法将传入的模板string 使用 variable_map进行解析，替换模板变量，返回str """

    my_template = string.Template(encode_unicode_bytes(templated_string))
    my_escaped_dict = dict(map(lambda x: (x[0], encode_unicode_bytes(x[1])), variable_map.items()))
    templated = my_template.safe_substitute(my_escaped_dict)
    return templated


def safe_to_json(in_obj):
    """ Safely get dict from object if present for json dumping """
    if isinstance(in_obj, bytearray):
        return str(in_obj)
    if hasattr(in_obj, '__dict__'):
        return in_obj.__dict__
    try:
        return str(in_obj)
    except:
        return repr(in_obj)


def flatten_dictionaries(input):
    """ 将一个列表中的字典合成一个字典，如果传入的不是一个列表，则直接返回 """
    output = dict()
    if isinstance(input, list):
        for map in input:
            output.update(map)
    else:  # Not a list of dictionaries
        output = input
    return output


def lowercase_keys(input_dict):
    """ 如果传入字典，则将字典中的所有key转为str并降为小写 """
    if not isinstance(input_dict, dict):
        return input_dict
    safe = dict()
    for key, value in input_dict.items():
        safe[str(key).lower()] = value
    return safe


def safe_to_bool(input):
    """ 将输入转化成bool值，大小写不敏感。如果不是bool或者不是符合 'true' 或 'false' 的str，则抛出异常 """
    if isinstance(input, bool):
        return input
    elif isinstance(input, basestring) and input.lower() == u'false':
        return False
    elif isinstance(input, basestring) and input.lower() == u'true':
        return True
    else:
        raise TypeError('Input Object is not a boolean or string form of boolean!')


def coerce_to_string(val):
    if isinstance(val, unicode):
        return val
    elif isinstance(val, int):
        return unicode(val)
    elif isinstance(val, str):
        return val.decode('utf-8')
    else:
        raise TypeError("Input {0} is not a string or integer, and it needs to be!".format(val))


def coerce_string_to_ascii(val):
    if isinstance(val, unicode):
        return val.encode('ascii')
    elif isinstance(val, str):
        return val
    else:
        raise TypeError("Input {0} is not a string, string expected".format(val))


def coerce_http_method(val):
    myval = val
    if not isinstance(myval, basestring) or len(val) == 0:
        raise TypeError("Invalid HTTP method name: input {0} is not a string or has 0 length".format(val))
    if isinstance(myval, str):
        myval = myval.decode('utf-8')
    return myval.upper()


def coerce_list_of_ints(val):
    """ If single value, try to parse as integer, else try to parse as list of integer """
    if isinstance(val, list):
        return [int(x) for x in val]
    else:
        return [int(val)]
