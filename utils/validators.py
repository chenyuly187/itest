

class FailureException(Exception):
    """ Validate Failed """
    pass


def validate_in(a, b):
    """ assert a in b """
    _a = a.decode() if isinstance(a, bytes) else a
    _b = b.decode() if isinstance(b, bytes) else b
    if _a not in _b:
        raise FailureException('%s not found in %s ' % (_a, _b))


def validate_nin(a, b):
    """ assert a not in b """
    _a = a.decode() if isinstance(a, bytes) else a
    _b = b.decode() if isinstance(b, bytes) else b
    if a in b:
        raise FailureException('%s found in %s ' % (_a, _b))


def validate_eq(a, b):
    """ assert a == b """
    _a = a.decode() if isinstance(a, bytes) else a
    _b = b.decode() if isinstance(b, bytes) else b
    if a != b:
        raise FailureException('%s not equal to %s ' % (_a, _b))


def validate_neq(a, b):
    """ assert a != b """
    _a = a.decode() if isinstance(a, bytes) else a
    _b = b.decode() if isinstance(b, bytes) else b
    if a == b:
        raise FailureException('%s equal to %s ' % (_a, _b))


def validate_lt(a, b):
    """ assert a < b"""
    _a = a.decode() if isinstance(a, bytes) else a
    _b = b.decode() if isinstance(b, bytes) else b
    if a >= b:
        raise FailureException('%s not less then %s ' % (_a, _b))


def validate_gt(a, b):
    """ assert a > b"""
    _a = a.decode() if isinstance(a, bytes) else a
    _b = b.decode() if isinstance(b, bytes) else b
    if a <= b:
        raise FailureException('%s not greater then %s ' % (_a, _b))


def validate_leq(a, b):
    """ assert a <= b"""
    _a = a.decode() if isinstance(a, bytes) else a
    _b = b.decode() if isinstance(b, bytes) else b
    if a > b:
        raise FailureException('%s not less equal then %s ' % (_a, _b))


def validate_geq(a, b):
    """ assert a >= b"""
    _a = a.decode() if isinstance(a, bytes) else a
    _b = b.decode() if isinstance(b, bytes) else b
    if a < b:
        raise FailureException('%s not greater equal then %s ' % (_a, _b))


VALIDATORS = {
    "in": validate_in,
    "nin": validate_nin,
    "eq": validate_eq,
    "neq": validate_neq,
    "lt": validate_lt,
    "gt": validate_gt,
    "leq": validate_leq,
    "geq": validate_geq,
}

