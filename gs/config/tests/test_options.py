from unittest import main, TestSuite, makeSuite, TestCase

import zope.interface
from zope.schema import *
from zope.schema.interfaces import WrongType
from gs.option.converter import *
from gs.option.option import *
from gs.option.interfaces import IGSOptionConverter, IGSOption
from zope.component.factory import IFactory
from zope.component.interfaces import ComponentLookupError
from zope.component import provideAdapter, getMultiAdapter, getGlobalSiteManager, getUtility, createObject
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from Products.ZSQLAlchemy.ZSQLAlchemy import manage_addZSQLAlchemy
import Products.Five
import gs.option
from Zope2.App import zcml
from zope.site.folder import Folder, rootFolder

from Testing.ZopeTestCase import ZopeTestCase
from gs.option import queries, ComponentOptions

import random
import gs.option.sql
import database_setup as ds

class ITestOptions(zope.interface.Interface):
    text_id = Text()
    int_id = Int()
    bool_id = Bool()
    float_id = Float()
    
class ITestOptions2(zope.interface.Interface):
    int_id = Int()

class TestOptionsFactory(GSOptionConverterFactory):
    interface = ITestOptions

class TestOptionsFactory2(GSOptionConverterFactory):
    interface = ITestOptions2

class RDBBaseTest(ZopeTestCase):
    def afterSetUp(self):
        if not ds.dbSetupDone:
            ds.dbteardown()
            ds.dbsetup()
            ds.dbSetupDone = True
        
        ds.dbTable(gs.option.sql, "01_option.sql", ["option"])
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', gs.option)
        
        gsm = getGlobalSiteManager()
        gsm.registerUtility(factory=TestOptionsFactory, name="gs.option.tests.options")
        
        alchemy_adaptor = manage_addZSQLAlchemy(self.folder, 'zsqlalchemy')
        
        alchemy_adaptor.manage_changeProperties(hostname='localhost',
                                                port=5432,
                                                username=ds.DATABASE_USER,
                                                password='',
                                                dbtype='postgres',
                                                database=ds.DATABASE_NAME)
        
        self.da = alchemy_adaptor
        self.componentId = 'component_id'
        self.optionId = 'option_id'
        
class RDBBackendTest(RDBBaseTest):
    def test_01_OptionQuery(self):
        optionQuery = queries.OptionQuery(self.da,
                                          self.componentId,
                                          self.optionId)
        
    def test_02_SetGetOption(self):
        optionQuery = queries.OptionQuery(self.da,
                                          self.componentId,
                                          self.optionId)
        rid1 = unicode(random.random())
        rid2 = unicode(random.random())
        rid3 = unicode(random.random())
        
        optionQuery.set(rid1)
        optionQuery.set(rid2,'site')
        optionQuery.set(rid3,'site','group')
        
        self.assertEqual(optionQuery.get(),rid1)
        self.assertEqual(optionQuery.get('site'),rid2)
        self.assertEqual(optionQuery.get('site','group'),rid3)

class RDBOptionTest(RDBBaseTest):
    def test_01_OptionStorageNoQualifiers(self):
        option = createObject('groupserver.Option', self.folder, 'gs.option.tests', 'int_id')
        self.assertEquals(option.get(), None)
        self.assertEquals(option.set(21), None)
        self.assertEquals(option.get(), 21)
        
    def test_02_OptionStorageQualified(self):
        option = createObject('groupserver.Option', self.folder, 'gs.option.tests', 'int_id')

        self.assertEquals(option.get('someSite'), None)
        self.assertEquals(option.get('someSite', 'someGroup'), None)
        
        self.assertEquals(option.set(42, 'someSite'), None)
        self.assertEquals(option.set(84, 'someSite', 'someGroup'), None)
        
        self.assertEquals(option.get('someSite'), 42)
        self.assertEquals(option.get('someSite', 'someGroup'), 84)
        
        # note: we reset the table between tests, so this should return None
        self.assertEquals(option.get(), None)
        
    def test_03_OptionConverter(self):
        option = createObject('groupserver.Option', self.folder, 'gs.option.tests', 'int_id')

        self.assertRaises(WrongType, option.set, '42', None)
    
class BasicOptionTest(TestCase):
    def setUp(self):
        self.gsm = getGlobalSiteManager()
        
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', gs.option)
        
        self.gsm.registerUtility(factory=GSRAMOptionFactory, name="groupserver.Option")
        self.gsm.registerUtility(factory=TestOptionsFactory, name="gs.option.tests.options")
        self.gsm.registerUtility(factory=TestOptionsFactory2, name="gs.option.tests2.options")
        
    def test_01_OptionConverterFromOption(self):
        option = createObject("groupserver.Option", None, 'gs.option.tests', 'int_id')
        assert isinstance(option.converter, GSIntConverterBasic)

    def test_03_OptionFactoryFailedComponentLookup(self):
        self.assertRaises(ComponentLookupError, createObject, "groupserver.Option", None, "gs.option.tests.thisdoesntexist", "int_id")
        
    def test_04_OptionStorageNoQualifiers(self):
        option = createObject("groupserver.Option", None, 'gs.option.tests', 'int_id')

        self.assertEquals(option.get(), None)
        self.assertEquals(option.set(21), None)
        self.assertEquals(option.get(), 21)
        
    def test_05_OptionStorageQualified(self):
        option = createObject("groupserver.Option", None, 'gs.option.tests', 'int_id')

        self.assertEquals(option.get('someSite'), None)
        self.assertEquals(option.get('someSite','someGroup'), None)
        
        self.assertEquals(option.set(42,'someSite'), None)
        self.assertEquals(option.set(84,'someSite', 'someGroup'), None)
        
        self.assertEquals(option.get('someSite'), 42)
        self.assertEquals(option.get('someSite', 'someGroup'), 84)
        
        # because we don't reset the storage between tests, this should return
        # the result of the set in test_04.
        self.assertEquals(option.get(), 21)
        
    def test_06_OptionConverter(self):
        option = createObject("groupserver.Option", None, 'gs.option.tests', 'int_id')
        
        self.assertRaises(WrongType, option.set, '42', None)

class ComponentOptionsHelperTest(TestCase):
    def setUp(self):
        self.gsm = getGlobalSiteManager()
        
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', gs.option)
        
        self.gsm.registerUtility(factory=GSRAMOptionFactory, provided=IGSOption)
        self.gsm.registerUtility(factory=TestOptionsFactory, provided=IGSOptionConverter, name="gs.option.tests.options")
        self.gsm.registerUtility(factory=TestOptionsFactory2, provided=IGSOptionConverter, name="gs.option.tests2.options")

    def test_01_OptionsGet(self):
        options = ComponentOptions(None, "gs.option.tests")
        # set in previous test set
        self.assertEquals(options.get("int_id"), 21)
        self.assertEquals(options.set(42,"int_id"), None)
        self.assertEquals(options.get("int_id"), 42)
        

def test_suite():
   suite = TestSuite()
   suite.addTest(makeSuite(RDBBackendTest))
   suite.addTest(makeSuite(RDBOptionTest))
   suite.addTest(makeSuite(BasicOptionTest))
   suite.addTest(makeSuite(ComponentOptionsHelperTest))
   
   return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
