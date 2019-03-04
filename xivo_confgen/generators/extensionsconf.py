# -*- coding: utf-8 -*-
# Copyright 2011-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from StringIO import StringIO

from xivo import OrderedConf, xivo_helpers
from xivo_dao import asterisk_conf_dao
from xivo_dao.resources.ivr import dao as ivr_dao


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
    'cctoggle': 'GoSub(cctoggle,s,1())',
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


class ExtensionGenerator(object):
    def __init__(self, exten_row):
        self._exten_row = exten_row


class UserExtensionGenerator(ExtensionGenerator):

    def generate(self):
        return {
            'context': self._exten_row['context'],
            'exten': self._exten_row['exten'],
            'priority': '1',
            'action': 'GoSub(user,s,1({},,{}))'.format(self._exten_row['typeval'], self._exten_row['id']),
        }


class IncallExtensionGenerator(ExtensionGenerator):

    def generate(self):
        return {
            'tenant_uuid': self._exten_row['tenant_uuid'],
            'context': self._exten_row['context'],
            'exten': self._exten_row['exten'],
            'priority': '1',
            'action': 'GoSub(did,s,1({},))'.format(self._exten_row['typeval']),
        }


class GenericExtensionGenerator(ExtensionGenerator):

    def generate(self):
        return {
            'context': self._exten_row['context'],
            'exten': self._exten_row['exten'],
            'priority': '1',
            'action': 'GoSub({},s,1({},))'.format(self._exten_row['type'], self._exten_row['typeval']),
        }


extension_generators = {
    'user': UserExtensionGenerator,
    'incall': IncallExtensionGenerator,
    'did': IncallExtensionGenerator,
}


class ExtensionsConf(object):

    def __init__(self, contextsconf, hint_generator, tpl_helper):
        self.contextsconf = contextsconf
        self.hint_generator = hint_generator
        self._tpl_helper = tpl_helper

    def generate(self, output):
        options = output

        if self.contextsconf is not None:
            # load context templates
            conf = OrderedConf.OrderedRawConf(filename=self.contextsconf)
            if conf.has_conflicting_section_names():
                raise ValueError("%s has conflicting section names" % self.contextsconf)
            if not conf.has_section('template'):
                raise ValueError("Template section doesn't exist in %s" % self.contextsconf)

        # hints & features (init)
        extenfeature_names = (
            'bsfilter',
            'callmeetme',
            'calluser',
            'fwdbusy',
            'fwdrna',
            'fwdunc',
            'phoneprogfunckey',
            'vmusermsg',
        )
        extenfeatures = asterisk_conf_dao.find_extenfeatures_settings(features=extenfeature_names)
        xfeatures = {extenfeature.typeval: {'exten': extenfeature.exten,
                                            'commented': extenfeature.commented}
                     for extenfeature in extenfeatures}

        # foreach active context
        for ctx in asterisk_conf_dao.find_context_settings():
            # context name preceded with '!' is ignored
            if conf and conf.has_section('!%s' % ctx['name']):
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
            for row in asterisk_conf_dao.find_contextincludes_settings(ctx['name']):
                print >> options, "include = %s" % row['include']
            print >> options

            # objects extensions (user, group, ...)
            for exten_row in asterisk_conf_dao.find_exten_settings(ctx['name']):
                exten_generator = extension_generators.get(exten_row['type'], GenericExtensionGenerator)
                exten = exten_generator(exten_row).generate()
                self.gen_dialplan_from_template(tmpl, exten, options)

            # conference supervision
            conferences = asterisk_conf_dao.find_exten_conferences_settings(context_name=ctx['name'])
            if len(conferences) > 0:
                print >> options, "\n; conferences supervision"

            for conference in conferences:
                if conference['exten'] is not None:
                    exten = xivo_helpers.clean_extension(conference['exten'])
                else:
                    continue

            self._generate_hints(ctx['name'], options)

        print >> options, self._extensions_features(conf, xfeatures)
        self._generate_ivr(output)

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

        for exten in asterisk_conf_dao.find_exten_xivofeatures_setting():
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

            line = line.replace('%%CONTEXT%%', str(exten.get('context', '')))
            line = line.replace('%%EXTEN%%', str(exten.get('exten', '')))
            line = line.replace('%%PRIORITY%%', str(exten.get('priority', '')))
            line = line.replace('%%ACTION%%', str(exten.get('action', '')))
            line = line.replace('%%TENANT_UUID%%', str(exten.get('tenant_uuid', '')))

            print >> output, prefix, line
        print >> output

    def _generate_hints(self, context, output):
        for line in self.hint_generator.generate(context):
            print >> output, line

    def _generate_ivr(self, output):
        for ivr in ivr_dao.find_all_by():
            template_context = {'ivr': ivr}
            template = self._tpl_helper.get_customizable_template('asterisk/extensions/ivr', ivr.id)
            template.generate(template_context, output)
            print >> output
