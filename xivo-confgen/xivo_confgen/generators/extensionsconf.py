# -*- coding: utf-8 -*-

# Copyright (C) 2011-2013 Avencall
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

import re
from StringIO import StringIO
from xivo import OrderedConf, xivo_helpers
from xivo_dao import callfilter_dao, user_dao
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.exception import ElementNotExistsError


DEFAULT_EXTENFEATURES = {
    'paging': 'GoSub(paging,s,1(${EXTEN:3}))',
    'autoprov': 'GoSub(autoprov,s,1())',
    'incallfilter': 'GoSub(incallfilter,s,1())',
    'phoneprogfunckey': 'GoSub(phoneprogfunckey,s,1(${EXTEN:0:4},${EXTEN:4}))',
    'phonestatus': 'GoSub(phonestatus,s,1())',
    'pickup': 'Pickup(${EXTEN:2}%${CONTEXT}@PICKUPMARK)',
    'recsnd': 'GoSub(recsnd,s,1(wav))',
    'vmboxmsgslt': 'GoSub(vmboxmsg,s,1(${EXTEN:3}))',
    'vmboxpurgeslt': 'GoSub(vmboxpurge,s,1(${EXTEN:3}))',
    'vmboxslt': 'GoSub(vmbox,s,1(${EXTEN:3}))',
    'vmusermsg': 'GoSub(vmusermsg,s,1())',
    'vmuserpurge': 'GoSub(vmuserpurge,s,1())',
    'vmuserpurgeslt': 'GoSub(vmuserpurge,s,1(${EXTEN:3}))',
    'vmuserslt': 'GoSub(vmuser,s,1(${EXTEN:3}))',
    'agentstaticlogin': 'GoSub(agentstaticlogin,s,1(${EXTEN:3}))',
    'agentstaticlogoff': 'GoSub(agentstaticlogoff,s,1(${EXTEN:3}))',
    'agentstaticlogtoggle': 'GoSub(agentstaticlogtoggle,s,1(${EXTEN:3}))',
    'bsfilter': 'GoSub(bsfilter,s,1(${EXTEN:3}))',
    'callgroup': 'GoSub(group,s,1(${EXTEN:4}) )',
    'calllistening': 'GoSub(calllistening,s,1())',
    'callmeetme': 'GoSub(meetme,s,1(${EXTEN:4}))',
    'callqueue': 'GoSub(queue,s,1(${EXTEN:4}))',
    'callrecord': 'GoSub(callrecord,s,1() )',
    'calluser': 'GoSub(user,s,1(${EXTEN:4}))',
    'directoryaccess': 'Directory(${CONTEXT})',
    'enablednd': 'GoSub(enablednd,s,1())',
    'enablevm': 'GoSub(enablevm,s,1())',
    'enablevmslt': 'GoSub(enablevm,s,1(${EXTEN:3}))',
    'fwdundoall': 'GoSub(fwdundoall,s,1())',
    'fwdbusy': 'GoSub(feature_forward,s,1(busy,${EXTEN:3}))',
    'fwdrna': 'GoSub(feature_forward,s,1(rna,${EXTEN:3}))',
    'fwdunc': 'GoSub(feature_forward,s,1(unc,${EXTEN:3}))',
}


class ExtensionsConf(object):
    def __init__(self, backend, contextsconf):
        self.backend = backend
        self.contextsconf = contextsconf

    def generate(self, output):
        self.generate_voice_menus(self.backend.voicemenus.all(commented=0, order='name'), output)

        options = output
        conf = None

        # load context templates
        if hasattr(self, 'contextsconf'):
            conf = OrderedConf.OrderedRawConf(filename=self.contextsconf)
            if conf.has_conflicting_section_names():
                raise ValueError("%s has conflicting section names" % self.contextsconf)
            if not conf.has_section('template'):
                raise ValueError("Template section doesn't exist")

        # hints & features (init)
        xfeatures = {
            'bsfilter': {},
            'callgroup': {},
            'callmeetme': {},
            'callqueue': {},
            'calluser': {},
            'fwdbusy': {},
            'fwdrna': {},
            'fwdunc': {},
            'phoneprogfunckey': {},
            'vmusermsg': {}}

        extensions = self.backend.extenfeatures.all(features=xfeatures.keys())
        xfeatures.update(dict([x['typeval'], {'exten': x['exten'], 'commented': x['commented']}] for x in extensions))

        # foreach active context
        for ctx in self.backend.contexts.all(commented=False, order='name', asc=False):
            # context name preceded with '!' is ignored
            if conf.has_section('!' + ctx['name']):
                continue

            print >> options, "\n[%s]" % ctx['name']

            if conf.has_section(ctx['name']):
                section = ctx['name']
            elif conf.has_section('type:%s' % ctx['contexttype']):
                section = 'type:%s' % ctx['contexttype']
            else:
                section = 'template'

            tmpl = []
            for option in conf.iter_options(section):
                if option.get_name() == 'objtpl':
                    tmpl.append(option.get_value())
                    continue

                print >> options, "%s = %s" % (option.get_name(), option.get_value().replace('%%CONTEXT%%', ctx['name']))

            # context includes
            for row in self.backend.contextincludes.all(context=ctx['name'], order='priority'):
                print >> options, "include = %s" % row['include']
            print >> options

            # objects extensions (user, group, ...)
            for exten in self.backend.extensions.all(context=ctx['name'], commented=False, order='exten'):
                if exten['type'] == 'user':
                    try:
                        user = user_dao.get(int(exten['typeval']))
                        ringseconds = user.ringseconds if user.ringseconds else ''
                        language = user.language if user.language else ''
                        line = line_services.get_by_user_id(user.id)
                        exten['action'] = 'GoSub(user,s,1(%s,%s,%s,%s))' % (user.id, line.id, ringseconds, language)
                    except (ElementNotExistsError, LookupError):
                        continue
                elif exten['type'] == 'group':
                    exten['action'] = 'GoSub(group,s,1(%s,))' % exten['typeval']
                elif exten['type'] == 'queue':
                    exten['action'] = 'GoSub(queue,s,1(%s,))' % exten['typeval']
                elif exten['type'] == 'meetme':
                    exten['action'] = 'GoSub(meetme,s,1(%s,))' % exten['typeval']
                elif exten['type'] == 'incall':
                    exten['action'] = 'GoSub(did,s,1(%s,))' % exten['exten']
                elif exten['type'] == 'outcall':
                    exten['action'] = 'GoSub(outcall,s,1(%s,))' % exten['typeval']
                else:
                    continue

                self.gen_dialplan_from_template(tmpl, exten, options)

            # phone (user) hints
            hints = self.backend.hints.all(context=ctx['name'])
            if len(hints) > 0:
                print >> options, "; phones hints"

            for hint in hints:
                xid = hint['id']
                number = hint['number']
                name = hint['name']
                proto = hint['protocol'].upper()
                if proto == 'IAX':
                    proto = 'IAX2'

                interface = "%s/%s" % (proto, name)
                if proto == 'CUSTOM':
                    interface = name

                if number:
                    print >> options, "exten = %s,hint,%s" % (number, interface)

                if not xfeatures['calluser'].get('commented', 1):
                    print >> options, "exten = %s,hint,%s" % (xivo_helpers.fkey_extension(
                        xfeatures['calluser']['exten'], (xid,)),
                        interface)

                if not xfeatures['vmusermsg'].get('commented', 1) and int(hint['enablevoicemail']) \
                     and hint['uniqueid']:
                    if proto == 'CUSTOM':
                        print >> options, "exten = %s%s,hint,%s" % (xfeatures['vmusermsg']['exten'], number, interface)

            # objects(user,group,...) supervision
            phonesfk = self.backend.phonefunckeys.all(context=ctx['name'])
            if len(phonesfk) > 0:
                print >> options, "\n; phones supervision"

            xset = set()
            for pkey in phonesfk:
                xtype = pkey['typeextenumbersright']
                calltype = "call%s" % xtype

                if pkey['exten'] is not None:
                    exten = xivo_helpers.clean_extension(pkey['exten'])
                elif calltype in xfeatures and not xfeatures[calltype].get('commented', 1):
                    exten = xivo_helpers.fkey_extension(
                        xfeatures[calltype]['exten'],
                        (pkey['typevalextenumbersright'],))
                else:
                    continue

                xset.add((exten, ("MeetMe:%s" if xtype == 'meetme' else "Custom:%s") % exten))

            for hint in xset:
                print >> options, "exten = %s,hint,%s" % hint

            # BS filters supervision
            callfiltermemberids = callfilter_dao.get_secretaries_id_by_context(ctx['name'])

            if len(callfiltermemberids) > 0:
                bsfilter_exten = xfeatures['bsfilter'].get('exten')
                print >> options, "\n; BS filters supervision"
                for callfiltermemberid in callfiltermemberids:
                    exten = xivo_helpers.fkey_extension(bsfilter_exten, callfiltermemberid)
                    print >> options, "exten = %s,hint,Custom:%s" % (exten, exten)

            # prog funckeys supervision
            progfunckeys = self.backend.progfunckeys.all(context=ctx['name'])

            extens = set()
            for k in progfunckeys:
                exten = k['exten']

                if exten is None and k['typevalextenumbersright'] is not None:
                    exten = "*%s" % k['typevalextenumbersright']

                extens.add(xivo_helpers.fkey_extension(xfeatures['phoneprogfunckey'].get('exten'),
                    (k['iduserfeatures'], k['leftexten'], exten)))

            if len(extens) > 0:
                print >> options, "\n; prog funckeys supervision"
                for exten in extens:
                    print >> options, "exten = %s,hint,Custom:%s" % (exten, exten)

        print >> options, self._extensions_features(conf, xfeatures)
        return options.getvalue()

    def _extensions_features(self, conf, xfeatures):
        options = StringIO()
        # XiVO features
        context = 'xivo-features'
        cfeatures = []
        tmpl = []

        print >> options, "\n[%s]" % context
        for option in conf.iter_options(context):
            if option.get_name() == 'objtpl':
                tmpl.append(option.get_value())
                continue

            print >> options, "%s = %s" % (option.get_name(), option.get_value().replace('%%CONTEXT%%', context))
            print >> options

        for exten in self.backend.extensions.all(context='xivo-features', commented=False):
            name = exten['typeval']
            if name in DEFAULT_EXTENFEATURES:
                exten['action'] = DEFAULT_EXTENFEATURES[name]
                self.gen_dialplan_from_template(tmpl, exten, options)

        for x in ('busy', 'rna', 'unc'):
            fwdtype = "fwd%s" % x
            if not xfeatures[fwdtype].get('commented', 1):
                exten = xivo_helpers.clean_extension(xfeatures[fwdtype]['exten'])
                cfeatures.extend([
                    "%s,1,Set(XIVO_BASE_CONTEXT=${CONTEXT})" % exten,
                    "%s,n,Set(XIVO_BASE_EXTEN=${EXTEN})" % exten,
                    "%s,n,Gosub(feature_forward,s,1(%s))\n" % (exten, x),
                ])

        if cfeatures:
            print >> options, "exten = " + "\nexten = ".join(cfeatures)

        return options.getvalue()

    def gen_dialplan_from_template(self, template, exten, output):
        if 'priority' not in exten:
            exten['priority'] = 1

        for line in template:
            prefix = 'exten =' if line.startswith('%%EXTEN%%') else 'same  =    '

            def varset(matchObject):
                return str(exten.get(matchObject.group(1).lower(), ''))
            line = re.sub('%%([^%]+)%%', varset, line)
            print >> output, prefix, line
        print >> output

    def generate_voice_menus(self, voicemenus, output):
        for vm_context in voicemenus:
            print >> output, "[voicemenu-%s]" % vm_context['name']
            for act in self.backend.extensions.all(context='voicemenu-' + vm_context['name'], commented=0):
                values = (act['exten'], act['priority'], act['app'], act['appdata'].replace('|', ','))
                print >> output, "exten = %s,%s,%s(%s)" % values
            print >> output

    @staticmethod
    def _build_sorted_bsfilter(query_result):
        numbers = []
        for bsfilter in query_result:
            if bsfilter['bsfilter'] == 'secretary':
                boss, secretary = bsfilter['exten'], bsfilter['number']
            elif bsfilter['bsfilter'] == 'boss':
                boss, secretary = bsfilter['number'], bsfilter['exten']
            else:
                pass
            numbers.append((boss, secretary))
        return set(numbers)

    @classmethod
    def new_from_backend(cls, backend, contextconfs):
        return cls(backend, contextconfs)
