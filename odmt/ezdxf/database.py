# Purpose: database module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from collections import OrderedDict


def factory(debug=False):
    return DebugDB() if debug else EntityDB()

from .handle import HandleGenerator


class SimpleDB(dict):
    def __init__(self):
        self.handles = HandleGenerator()

    def add_tags(self, tags):
        try:
            handle = tags.get_handle()
        except ValueError:
            handle = self.handles.next()
        self.__setitem__(handle, tags)
        return handle


class EntityDB(object):
    """ A simple key/value database a.k.a. dict(), but can be replaced other
    classes that implements all of the methods of `EntityDB`. The entities
    have no order.

    The Data Model

    Every entity/object, except tables and sections, are represented as
    tag-list (see Tags Class), this lists are stored in the drawing-associated
    database, database-key is the 'handle' tag (code == 5 or 105).

    For the entity/object manipulation this tag-list will be wrapped into
    separated classes, which are generated by the dxffactory-object.
    The dxffactory-object generates DXF-Version specific wrapper classes.

    """
    def __init__(self):
        self._database = {}
        self.handles = HandleGenerator()

    def __delitem__(self, key):
        del self._database[key]

    def __getitem__(self, handle):
        return self._database[handle]

    def __setitem__(self, handle, entity):
        self._database[handle] = entity

    def __contains__(self, handle):
        """ Database contains handle? """
        return handle in self._database

    def __len__(self):
        """ Count of database items. """
        return len(self._database)

    def __iter__(self):
        """ Iterate over all handles. """
        return iter(self._database.keys())

    def keys(self):
        """ Iterate over all handles. """
        return self._database.keys()

    def values(self):
        """ Iterate over all entities. """
        return self._database.values()

    def items(self):
        """ Iterate over all (handle, entities) pairs. """
        return self._database.items()

    def add_tags(self, tags):
        try:
            handle = tags.get_handle()
        except ValueError:
            handle = self.handles.next()
        self.__setitem__(handle, tags)
        return handle


class DebugDB(EntityDB):
    TAGFMT = "(%d, %s)"

    def __init__(self):
        self._database = OrderedDict()
        self._collisions = {}
        self._stream = None
        self._verbose = True

    def __setitem__(self, handle, entity):
        if handle in self:
            collisions = self._collisions.setdefault(handle, [])
            collisions.append(self[handle])
        super(DebugDB, self).__setitem__(handle, entity)

    def _setparams(self, stream, verbose):
        self._stream = stream
        self._verbose = verbose

    def printtags(self, tags):
        def tostring(tags):
            return " ".join((self.TAGFMT % tag for tag in tags))

        if self._verbose:
            self.println(str(tags))
        else:
            self.println(tostring(tags))

    def println(self, text=""):
        self._stream.write(text + '\n')

    def dumpcollisions(self, stream, verbose=True):
        def dump_entry(handle):
            self.println()
            self.println("Handle: %s" % handle)
            collisions = self._collisions[handle]
            dump_collision(collisions)

        def dump_collision(collisions):
            self.println("Count: %d" % len(collisions))
            for tags in collisions:
                self.printtags(tags)

        self._setparams(stream, verbose)
        self.println("Database contains %d collisions." % len(self._collisions))
        for handle in self._collisions:
            dump_entry(handle)

    def dumpcontent(self, stream, verbose=True):
        def dump_entry(handle):
            self.println()
            self.println("Handle: %s" % handle)
            self.printtags(self[handle])

        self._setparams(stream, verbose)
        self.println("Database contains %d entries." % len(self))
        for handle in self:
            dump_entry(handle)
