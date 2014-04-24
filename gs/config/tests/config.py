# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from unittest import TestCase
import gs.config.config


class TestConfig(TestCase):
    '''Test the gs.config.config module'''

    def test_bool_true(self):
        vals = ('true', 'yes', 'on')
        for v in vals:
            r = gs.config.config.bool_(v)
            self.assertTrue(r)

    def test_bool_false(self):
        vals = ('false', 'no', 'off')
        for v in vals:
            r = gs.config.config.bool_(v)
            self.assertFalse(r)

    def test_bool_garbage(self):
        self.assertRaises(ValueError, gs.config.config.bool_, 'I am a fish.')
