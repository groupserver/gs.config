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
from mock import MagicMock
import gs.config.config


class TestBool(TestCase):
    '''Test the gs.config.config.bool_ function'''

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
        self.assertRaises(ValueError, gs.config.config.bool_, 'Ethyl the frog.')


class FakeRequest(object):
    '''A fake request-object, for testing gs.config.config.getInstanceId.'''

    def get(self, header, default):
        return 'parana'


class FakeRequestDef(object):
    '''A fake request-object, for testing gs.config.config.getInstanceId,
    which returns the default for the get-method.'''

    def get(self, header, default):
        return default


class TestGetInstanceId(TestCase):
    '''Test the gs.config.config.getInstance function'''

    def setUp(self):
        req = FakeRequest()
        gs.config.config.getRequest = MagicMock(return_value=req)
        self.oldUsingZope = gs.config.config.USINGZOPE

    def tearDown(self):
        gs.config.config.USINGZOPE = self.oldUsingZope

    def test_getInstance_no_zope(self):
        gs.config.config.USINGZOPE = False
        r = gs.config.config.getInstanceId()
        self.assertEqual('default', r)

    def test_getInstance_zope(self):
        gs.config.config.USINGZOPE = True
        r = gs.config.config.getInstanceId()
        self.assertEqual(1, gs.config.config.getRequest.call_count)
        self.assertEqual('parana', r)

    def test_getInstance_zope_no_header(self):
        gs.config.config.USINGZOPE = True
        req = FakeRequestDef()
        gs.config.config.getRequest = MagicMock(return_value=req)
        r = gs.config.config.getInstanceId()
        self.assertEqual(1, gs.config.config.getRequest.call_count)
        self.assertEqual('default', r)
