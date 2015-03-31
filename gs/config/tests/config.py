# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014, 2015 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
import codecs
from os import (remove, mkdir)
from os.path import join as path_join
from shutil import rmtree
from tempfile import (NamedTemporaryFile, mkdtemp)
from unittest import TestCase
from mock import (MagicMock, patch)
import gs.config.config
from gs.config.errors import ConfigNoSectionError, ConfigNoOptionError


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
        self.assertRaises(ValueError, gs.config.config.bool_,
                          'Ethyl the frog.')


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


class TestConfig(TestCase):
    config = '''[config-default]
show = EthylTheFrog
parana = brothers

[show-EthylTheFrog]
tonight = violence
toadTheWetSprocket = no

[parana-brothers]
twins = true
names =
  Dirk
  Dinsdale
likes = Boxing and putting the boot in.
age = 12
'''

    def setUp(self):
        self.oldUsingZope = gs.config.config.USINGZOPE

    def tearDown(self):
        gs.config.config.USINGZOPE = self.oldUsingZope

    def test_no_config(self):
        '''Test that we geta a ConfigPathError if there is no pointer to the
        config file.'''
        gs.config.config.USINGZOPE = False
        self.assertRaises(gs.config.config.ConfigPathError,
                          gs.config.config.Config, ('default', ))

    def get_config_file(self):
        with NamedTemporaryFile('w', delete=False) as tmp:
            retval = tmp.name
            tmp.write(self.config)
        return retval

    @staticmethod
    def del_config_file(filename):
        try:
            remove(filename)
        except OSError:
            pass

    def test_missing_section(self):
        '''Test that we get a ConfigSetError if the config file exists,
        but it lacks the section.'''
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()
        self.assertRaises(gs.config.config.ConfigSetError,
                          gs.config.config.Config, 'parrot',
                          configpath=configFile)
        self.del_config_file(configFile)

    def test_init(self):
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()
        c = gs.config.config.Config('default', configpath=configFile)
        self.assertEqual(c.configset, 'default')
        self.assertEqual(c.keys(), ['show', 'parana'])
        self.del_config_file(configFile)

    def test_set_schema(self):
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()
        c = gs.config.config.Config('default', configpath=configFile)
        s = {'twins': bool, 'names': str, 'likes': str}
        c.set_schema('parana', s)
        self.assertEqual(s, c.schema['parana'])
        self.del_config_file(configFile)

    def val_test(self, d, name, expected):
        self.assertIn(name, d)
        self.assertEqual(d[name], expected)

    def test_get(self):
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()
        c = gs.config.config.Config('default', configpath=configFile)
        s = {'twins': bool, 'names': str, 'likes': str, 'age': int}
        c.set_schema('parana', s)

        p = c.get('parana')
        self.val_test(p, 'twins', True)
        self.val_test(p, 'names', '\nDirk\nDinsdale')
        self.val_test(p, 'likes', 'Boxing and putting the boot in.')
        self.val_test(p, 'age', 12)

        self.del_config_file(configFile)

    def test_get_no_config(self):
        '''Test getting that getting the "wrong" config raises an error.'''
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()
        c = gs.config.config.Config('default', configpath=configFile)
        s = {'twins': bool, 'names': str, 'likes': str, 'age': int}
        c.set_schema('parana', s)

        self.assertRaises(ConfigNoSectionError, c.get, 'frog')

    def test_get_no_option(self):
        '''Test getting that getting the "wrong" option raises an error.'''
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()
        c = gs.config.config.Config('default', configpath=configFile)
        s = {'twins': bool, 'names': str, 'likes': str, 'age': int,
             'violence': bool}
        c.set_schema('parana', s)

        p = c.get('parana')
        self.assertNotIn('violence', p)

    def test_get_dan(self):
        '''Test that getting an option that has no schema raises an
error. Named for Dan Randow, who found the issue'''
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()

        # Write an option to the end of the config file
        with codecs.open(configFile, 'a', encoding='utf-8') as outfile:
            outfile.write('violence = False\n')

        c = gs.config.config.Config('default', configpath=configFile)
        s = {'twins': bool, 'names': str, 'likes': str, 'age': int}
        c.set_schema('parana', s)

        with self.assertRaises(ConfigNoOptionError) as cm:
            c.get('parana')
        msg = str(cm.exception)
        self.assertIn('violence', msg)
        self.assertIn('parana', msg)

        self.del_config_file(configFile)

    def test_get_lax_parse(self):
        '''Test that getting an option that has no schema is fine if
lax-parsing is on (strict=False)'''
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()

        # Write an option to the end of the config file
        with codecs.open(configFile, 'a', encoding='utf-8') as outfile:
            outfile.write('violence = False\n')

        c = gs.config.config.Config('default', configpath=configFile)
        s = {'twins': bool, 'names': str, 'likes': str, 'age': int}
        c.set_schema('parana', s)

        p = c.get('parana', strict=False)
        default = 'Tonight on Ethyl the Frog we look at Violence'
        r = p.get('boot', default)
        self.assertEqual(default, r)

    def test_get_convert_errror(self):
        gs.config.config.USINGZOPE = False
        configFile = self.get_config_file()
        c = gs.config.config.Config('default', configpath=configFile)
        # Dicts do not work.
        s = {'twins': bool, 'names': dict, 'likes': str, 'age': int}
        c.set_schema('parana', s)

        self.assertRaises(gs.config.config.ConfigConvertError, c.get,
                          'parana')

    @patch('gs.config.config.getConfiguration')
    def test_instancehome_exists(self, mock_getConfig):
        'INSTANCE_HOME only exists'
        d = mkdtemp()
        e_etc = path_join(d, 'etc')
        mkdir(e_etc)
        gsconfPath = path_join(e_etc, 'gsconfig.ini')
        with codecs.open(gsconfPath, 'w', encoding='utf-8') as outfile:
            outfile.write(self.config)
        gs.config.config.USINGZOPE = True
        mockConfig = mock_getConfig()
        mockConfig.instancehome = d

        dNonExistant = mkdtemp()
        mockConfig.zopehome = dNonExistant

        r = gs.config.config.Config.get_zope_config()
        self.assertEqual(gsconfPath, r)
        rmtree(d)
        rmtree(dNonExistant)

    @patch('gs.config.config.getConfiguration')
    def test_zopehome_exists(self, mock_getConfig):
        'ZOME_HOME only exists'
        d = mkdtemp()
        e_etc = path_join(d, 'etc')
        mkdir(e_etc)
        gsconfPath = path_join(e_etc, 'gsconfig.ini')
        with codecs.open(gsconfPath, 'w', encoding='utf-8') as outfile:
            outfile.write(self.config)
        gs.config.config.USINGZOPE = True
        mockConfig = mock_getConfig()
        mockConfig.zopehome = d

        dNonExistant = mkdtemp()
        mockConfig.instancehome = dNonExistant

        r = gs.config.config.Config.get_zope_config()
        self.assertEqual(gsconfPath, r)
        rmtree(d)
        rmtree(dNonExistant)

    @patch('gs.config.config.getConfiguration')
    def test_instancehome_preferred(self, mock_getConfig):
        'INSTANCE_HOME is preferred over ZOME_HOME'
        d_zopeHome = mkdtemp()
        d_zopeHome_etc = path_join(d_zopeHome, 'etc')
        mkdir(d_zopeHome_etc)
        notGsconfPath = path_join(d_zopeHome_etc, 'gsconfig.ini')
        with codecs.open(notGsconfPath, 'w', encoding='utf-8') as outfile:
            outfile.write(self.config)
        gs.config.config.USINGZOPE = True
        mockConfig = mock_getConfig()
        mockConfig.zopehome = d_zopeHome

        d_instanceHome = mkdtemp()
        d_instanceHome_etc = path_join(d_instanceHome, 'etc')
        mkdir(d_instanceHome_etc)
        gsconfPath = path_join(d_instanceHome_etc, 'gsconfig.ini')
        with codecs.open(gsconfPath, 'w', encoding='utf-8') as outfile:
            outfile.write(self.config)
        mockConfig.instancehome = d_instanceHome

        r = gs.config.config.Config.get_zope_config()
        self.assertEqual(gsconfPath, r)
        rmtree(d_zopeHome)
        rmtree(d_instanceHome)

    @patch('gs.config.config.getConfiguration')
    def test_missing_zope_files(self, mock_getConfig):
        'Test we get a ConfigFileError if neither Zope config files exist'
        gs.config.config.USINGZOPE = True
        mockConfig = mock_getConfig()
        d_instanceHome = mkdtemp()
        mockConfig.instancehome = d_instanceHome
        d_zopeHome = mkdtemp()
        mockConfig.zopehome = d_zopeHome

        with self.assertRaises(gs.config.config.ConfigFileError):
            gs.config.config.Config.get_zope_config()

    def test_missing_file(self):
        emptyDir = mkdtemp()
        wrong = path_join(emptyDir, 'etc', 'gsconfig.ini')
        with self.assertRaises(gs.config.config.ConfigFileError):
            gs.config.config.Config('default', wrong)
        rmtree(emptyDir)
