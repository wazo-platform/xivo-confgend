# -*- coding: utf-8 -*-

# Copyright (C) 2010-2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import inspect
import warnings

from sqlalchemy import exc
from sqlalchemy.ext.sqlsoup import SqlSoup
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_, desc

warnings.simplefilter('ignore')


def mapped_set(self, key, value):
    self.__dict__[key] = value


def mapped_iterkeys(self):
    keys = sorted(filter(lambda x: x[0] != '_', self.__dict__))

    for k in keys:
        yield k

    return


def mapped_iteritems(self):
    keys = sorted(filter(lambda x: x[0] != '_', self.__dict__))

    for k in keys:
        yield (k, self.__dict__[k])

    return


def iterable(mode):
    def _iterable(f):
        def single_wrapper(*args, **kwargs):
            try:
                ret = f(*args, **kwargs)
            except exc.OperationalError:
                # reconnect & retry
                args[0].db.flush()
                ret = f(*args, **kwargs)

            if ret is not None:
                ret.__class__.__getitem__ = lambda self, key: self.__dict__[key]
                ret.__class__.iteritems = mapped_iteritems

            return ret

        def list_wrapper(*args, **kwargs):
            try:
                ret = f(*args, **kwargs)
            except exc.OperationalError:
                # reconnect & retry
                args[0].db.flush()
                ret = f(*args, **kwargs)

            if isinstance(ret, list) and len(ret) > 0:
                ret[0].__class__.__getitem__ = lambda self, key: self.__dict__[key]
                ret[0].__class__.__setitem__ = mapped_set
                ret[0].__class__.__contains__ = lambda self, key: self.__dict__.__contains__(key)
                ret[0].__class__.iteritems = mapped_iteritems
                ret[0].__class__.iterkeys = mapped_iterkeys
                ret[0].__class__.get = lambda self, key, dft: self.__dict__[key] if key in self.__dict__ else dft

            return ret

        def join_wrapper(*args, **kwargs):
            ret = f(*args, **kwargs)
            if isinstance(ret, list) and len(ret) > 0:
                def find(d, k):
                    # print d.keys, k, k in d, unicode(k) in d
                    return None
                ret[0].__class__.__getitem__ = lambda self, key: find(self.__dict__, key)

            return ret

        return locals()[mode + '_wrapper']
    return _iterable


class SpecializedHandler(object):
    def __init__(self, db, name):
        self.db = db
        self.name = name

    def execute(self, q):
        try:
            ret = self.db.engine.connect().execute(q)
        except exc.OperationalError:
            # reconnect & retry
            self.db.flush()
            ret = self.db.engine.connect().execute(q)

        return ret


class AgentQueueskillsHandler(SpecializedHandler):
    def all(self, *args, **kwargs):
        (_a, _f, _s) = [getattr(self.db, options)._table for options in ('agentqueueskill', 'agentfeatures', 'queueskill')]
        q = select(
            [_f.c.id, _s.c.name, _a.c.weight],
            and_(_a.c.agentid == _f.c.id, _a.c.skillid == _s.c.id)
        )
        q = q.order_by(_f.c.id)

        return self.execute(q).fetchall()


class QueuePenaltiesHandler(SpecializedHandler):
    def all(self, **kwargs):
        (_p, _pc) = [getattr(self.db, options)._table.c for options in ('queuepenalty', 'queuepenaltychange')]

        q = select(
            [_p.name, _pc.seconds, _pc.maxp_sign, _pc.maxp_value, _pc.minp_sign, _pc.minp_value],
            and_(
                _p.commented == 0,
                _p.id == _pc.queuepenalty_id
            )
        ).order_by(_p.name)

        return self.execute(q).fetchall()


class QObject(object):
    _translation = {
        'agentfeatures': ('agentfeatures',),

        'queues': ('queue',),
        'queuemembers': ('queuemember',),
        'queuepenalty': ('queuepenalty',),

        'agentqueueskills': AgentQueueskillsHandler,

        'queuepenalties': QueuePenaltiesHandler,
        'parkinglot': ('parkinglot',),
        'general': ('general',),
    }

    def __init__(self, db, name):
        self.db = db
        self.name = name

    @iterable('list')
    def all(self, commented=None, order=None, asc=True, **kwargs):
        _trans = self._translation.get(self.name, (self.name,))
        q = getattr(self.db, _trans[0])

        # # FILTERING
        conds = []
        if isinstance(commented, bool):
            conds.append(q.commented == int(commented))

        if len(_trans) > 1:
            for k, v in _trans[1].iteritems():
                conds.append(getattr(q, k) == v)

        for k, v in kwargs.iteritems():
            conds.append(getattr(q, k) == v)

        q = q.filter(and_(*conds))

        # # ORDERING
        if order is not None:
            if not asc:
                order = desc(order)
            q = q.order_by(order)

        return q.all()

    @iterable('single')
    def get(self, **kwargs):
        q = getattr(self.db, self._translation.get(self.name, (self.name,))[0])

        conds = []
        for k, v in kwargs.iteritems():
            conds.append(getattr(q, k) == v)
        return q.filter(and_(*conds)).first()


class XivoDBBackend(object):
    def __init__(self, uri):
        self.db = SqlSoup(uri,
                          session=scoped_session(sessionmaker(autoflush=True, expire_on_commit=False, autocommit=True)))

    def __getattr__(self, name):
        if not name in QObject._translation:
            raise KeyError(name)

        if inspect.isclass(QObject._translation[name]) and\
                issubclass(QObject._translation[name], SpecializedHandler):
            return QObject._translation[name](self.db, name)

        return QObject(self.db, name)
