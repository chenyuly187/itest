# -*- coding: utf-8 -*-


class Error(Exception):
    """Base package Exception."""
    pass


class FileException(Error):
    """Base file exception.Thrown when a file is not available."""
    pass


class FileTypeNotSupportException(FileException):
    pass


class DataFileNotAvailableException(FileException):
    """Thrown when data file not available."""
    pass


class SheetTypeError(Error):
    """Thrown when sheet type passed in not int or str."""
    pass


class SheetError(Error):
    """Thrown when specified sheet not exists."""
    pass


class DataError(Error):
    """Thrown when something wrong with the data."""
    pass


class ParameterError(Error):
    """Thrown when pass wrong parameter to a method."""
    pass


class UnSupportMethod(Error):
    """Thrown when http method not allowed."""
    pass


class EncryptError(Error):
    """Thrown when Encrypt Error, such as sign without private key or encrypt without salt."""
    pass
