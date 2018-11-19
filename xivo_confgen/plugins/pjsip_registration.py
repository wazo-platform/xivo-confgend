# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

# class copied from the sip_to_pjsip.py in the Asterisk repository
# https://raw.githubusercontent.com/asterisk/asterisk/master/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py


class Registration(object):
    """
    Class for parsing and storing information in a register line in sip.conf.
    """
    def __init__(self, line):
        self.parse(line)

        self.section = 'reg_' + self.host
        self.registration_fields = []

        self.auth_section = 'auth_reg_' + self.host
        self.auth_fields = []

        self._generate()

    def parse(self, line):
        """
        Initial parsing routine for register lines in sip.conf.

        This splits the line into the part before the host, and the part
        after the '@' symbol. These two parts are then passed to their
        own parsing routines
        """

        # register =>
        # [peer?][transport://]user[@domain][:secret[:authuser]]@host[:port][/extension][~expiry]

        prehost, at, host_part = line.rpartition('@')
        if not prehost:
            raise

        self.parse_host_part(host_part)
        self.parse_user_part(prehost)

    def parse_host_part(self, host_part):
        """
        Parsing routine for the part after the final '@' in a register line.
        The strategy is to use partition calls to peel away the data starting
        from the right and working to the left.
        """
        pre_expiry, sep, expiry = host_part.partition('~')
        pre_extension, sep, self.extension = pre_expiry.partition('/')
        self.host, sep, self.port = pre_extension.partition(':')

        self.expiry = expiry if expiry else '120'

    def parse_user_part(self, user_part):
        """
        Parsing routine for the part before the final '@' in a register line.
        The only mandatory part of this line is the user portion. The strategy
        here is to start by using partition calls to remove everything to
        the right of the user, then finish by using rpartition calls to remove
        everything to the left of the user.
        """
        self.peer = ''
        self.protocol = 'udp'
        protocols = ['udp', 'tcp', 'tls']
        for protocol in protocols:
            position = user_part.find(protocol + '://')
            if -1 < position:
                post_transport = user_part[position + 6:]
                self.peer, sep, self.protocol = user_part[:position + 3].rpartition('?')
                user_part = post_transport
                break

        colons = user_part.count(':')
        if (colons == 3):
            # :domainport:secret:authuser
            pre_auth, sep, port_auth = user_part.partition(':')
            self.domainport, sep, auth = port_auth.partition(':')
            self.secret, sep, self.authuser = auth.partition(':')
        elif (colons == 2):
            # :secret:authuser
            pre_auth, sep, auth = user_part.partition(':')
            self.secret, sep, self.authuser = auth.partition(':')
        elif (colons == 1):
            # :secret
            pre_auth, sep, self.secret = user_part.partition(':')
        elif (colons == 0):
            # No port, secret, or authuser
            pre_auth = user_part
        else:
            # Invalid setting
            raise

        self.user, sep, self.domain = pre_auth.partition('@')

    def _generate(self):
        """
        Write parsed registration data into a section in pjsip.conf

        Most of the data in self will get written to a registration section.
        However, there will also need to be an auth section created if a
        secret or authuser is present.

        General mapping of values:
        A combination of self.host and self.port is server_uri
        A combination of self.user, self.domain, and self.domainport is
          client_uri
        self.expiry is expiration
        self.extension is contact_user
        self.protocol will map to one of the mapped transports
        self.secret and self.authuser will result in a new auth section, and
          outbound_auth will point to that section.
        XXX self.peer really doesn't map to anything :(
        """

        if self.extension:
            self.registration_fields.append(('contact_user', self.extension))

        self.registration_fields.append(('expiration', self.expiry))
        self.registration_fields.append(('transport', 'transport-{}'.format(self.protocol)))

        if hasattr(self, 'secret') and self.secret:
            self.auth_fields.append(('password', self.secret))
            self.auth_fields.append(('username', getattr(self, 'authuser', None) or self.user))
            self.registration_fields.append(('outbound_auth', self.auth_section))

        client_uri = "sip:%s@" % self.user
        if self.domain:
            client_uri += self.domain
        else:
            client_uri += self.host

        if hasattr(self, 'domainport') and self.domainport:
            client_uri += ":" + self.domainport
        elif self.port:
            client_uri += ":" + self.port
        self.registration_fields.append(('client_uri', client_uri))

        server_uri = "sip:%s" % self.host
        if self.port:
            server_uri += ":" + self.port
        self.registration_fields.append(('server_uri', server_uri))
