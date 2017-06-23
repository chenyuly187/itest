# -*- coding: utf-8 -*-
import yaml
from xlrd import open_workbook
from utils.exceptions import DataFileNotAvailableException, DataError, SheetTypeError, SheetError
from xml.etree.ElementTree import ElementTree
from settings import *

logger = logging.getLogger('itest')


class ExcelReader(object):
    def __init__(self, book, sheet=0):
        """Read workbook

        :param book: work_book path.
        :param sheet: index of sheet or sheet name.
        """
        self.book_name = book
        self.sheet_locator = sheet

        self.book = self._book()
        self.sheet = self._sheet()

    def _book(self):
        try:
            work_book = open_workbook(self.book_name)
        except IOError as e:
            raise DataFileNotAvailableException(e)
        logger.debug('open workbook {0}'.format(self.book_name))
        return work_book

    def _sheet(self):
        """Return sheet"""
        if type(self.sheet_locator) not in [int, str]:
            raise SheetTypeError('Please pass in <type \'int\'> or <type \'str\'>, not {0}'.format(type(self.sheet_locator)))
        elif type(self.sheet_locator) == int:
            try:
                sheet = self.book.sheet_by_index(self.sheet_locator)  # by index
            except:
                raise SheetError('Sheet \'{0}\' not exists.'.format(self.sheet_locator))
        else:
            try:
                sheet = self.book.sheet_by_name(self.sheet_locator)  # by name
            except:
                raise SheetError('Sheet \'{0}\' not exists.'.format(self.sheet_locator))
        logger.debug('read sheet {0}'.format(self.sheet_locator))
        return sheet

    @property
    def title(self):
        """First row is title."""
        try:
            return self.sheet.row_values(0)
        except IndexError:
            raise DataError('This is a empty sheet, please check your file.')

    @property
    def data(self):
        """Return data in specified type:

            [{row1:row2},{row1:row3},{row1:row4}...]
        """
        sheet = self.sheet
        title = self.title
        data = list()

        # zip title and rows
        for col in range(1, sheet.nrows):
            s1 = sheet.row_values(col)
            data.append(dict(zip(title, s1)))
        return data

    @property
    def nums(self):
        """Return the number of cases."""
        return len(self.data)


class YamlReader(object):
    """Read yaml file"""
    def __init__(self, fname):
        self.fpath = fname
        self._yaml = None

    @property
    def yaml(self):
        if not self._yaml:
            self._yaml = self._read()
        return self._yaml

    def _read(self):
        logger.debug('read yaml file {}'.format(self.fpath))
        with open(self.fpath, 'rb') as f:
            al = yaml.safe_load_all(f)
            return list(al)


class XMLReader(object):

    def __init__(self, xml):
        self.xml = xml

        self.tree = self._tree()
        logger.debug('read file: {0}'.format(self.xml))

    def _tree(self):
        try:
            return ElementTree(file=self.xml)
        except IOError as e:
            raise DataFileNotAvailableException(e)

    def get_url(self, tag):
        """Get interface url.

        :param tag: xml tag name.
        :return: base_url + tag text.
        """
        return self.base_url + self.get_text(tag)

    def get_text(self, tag):
        """Get tag text.

        :param tag: xml tag name or xpath.
        :return: tag text.
        """
        tree = self.tree
        try:
            return tree.find(tag).text.strip()
        except AttributeError:
            raise DataError('\'{0}\' does not have \'{1}\' element.Check your file.'.format(self.xml, tag))

    def get_type(self, tag):
        """Get interface type.

        :param tag: xml tag name.
        :return: interface type.
        """
        return self.get_text('.//{0}/type'.format(tag))

    def get_method(self, tag):
        """Get interface type.

        :param tag: xml tag name.
        :return: interface method.
        """
        return self.get_text('.//{0}/method'.format(tag))

    def get_file(self, tag):
        return self.get_text('.//{0}/file'.format(tag))

    def get_sheet(self, tag):
        return self.get_text('.//{0}/sheet'.format(tag))

    @property
    def base_url(self):
        """Get <Base></Base> text if exists."""
        return self.get_text('Base')

    def get_tags(self):
        base = self.tree.find('Base')
        tags = list()
        for element in self.tree.getroot().getchildren():
            if element != base:
                tags.append(element.tag)
        return tags
