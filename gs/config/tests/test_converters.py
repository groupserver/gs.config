from unittest import main, TestSuite, makeSuite, TestCase

import zope.interface
from zope.schema import *
from zope.schema.interfaces import WrongType
from gs.option.converter import *
from gs.option.option import *
from gs.option.interfaces import IGSOptionConverter, IGSOption
from zope.component.factory import IFactory
from zope.component import provideAdapter, getMultiAdapter, getGlobalSiteManager, getUtility, createObject
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from Products.ZSQLAlchemy.ZSQLAlchemy import manage_addZSQLAlchemy
import Products.Five
import gs.option
from Zope2.App import zcml
from zope.site.folder import Folder, rootFolder

from Testing.ZopeTestCase import ZopeTestCase
from gs.option import queries

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

class ConverterTest(TestCase):
    def setUp(self):
        self.gsm = getGlobalSiteManager()
        
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', gs.option)
        
        self.gsm.registerUtility(factory=TestOptionsFactory, name="gs.option.tests.options")
        self.gsm.registerUtility(factory=TestOptionsFactory2, name="gs.option.tests2.options")
        
    def testOptionConverterFactory(self):
        option = createObject('groupserver.Option', None, 'gs.option.tests2', 'int_id')
        
        optionConverter = createObject("gs.option.tests.options", None, "text_id", option)
        assert isinstance(optionConverter, GSTextConverterBasic)
        
        optionConverter = createObject("gs.option.tests.options", None, "int_id", option)
        assert isinstance(optionConverter, GSIntConverterBasic)
    
    def testOptionConverterFromOption(self):
        option = createObject('groupserver.Option', None, 'gs.option.tests', 'int_id')
        assert isinstance(option.converter, GSIntConverterBasic)
  
class BaseConverterTest(TestCase):
    def setUp(self):
        # setup the converter adapters and option factory registered in the
        # gs.option -> configure.zcml
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('configure.zcml', gs.option)
        
        # register an option converter factory for the test case
        gsm = getGlobalSiteManager()
        gsm.registerUtility(factory=TestOptionsFactory, name="gs.option.tests.options")
        
        self._setupOption()
  
class IntTest(BaseConverterTest):
    def _setupOption(self):
        self.option = createObject('groupserver.Option', None, 'gs.option.tests', 'int_id')

    def testConvertToSchemaValue(self):
        self.assertEqual(type(self.option.converter.toSchemaValue('1')), int)
        self.assertEqual(type(self.option.converter.toSchemaValue('1'*100)), long)
        
    def testConvertToStorageValue(self):
        self.assertEqual(type(self.option.converter.toStorageValue(1)), unicode)
        self.assertEqual(type(self.option.converter.toStorageValue(10**100)), unicode)

    def testFailValidation(self):
        self.assertRaises(WrongType, self.option.converter.toStorageValue, 1.0)
        self.assertRaises(WrongType, self.option.converter.toStorageValue, '1')
        self.assertRaises(WrongType, self.option.converter.toStorageValue, u'1')
        self.assertRaises(WrongType, self.option.converter.toStorageValue, [1,2,3])
        self.assertRaises(WrongType, self.option.converter.toStorageValue, (1,2,3))
        self.assertRaises(WrongType, self.option.converter.toStorageValue, {'1':2})
        
class BoolTest(BaseConverterTest):
    def _setupOption(self):
        self.option = createObject('groupserver.Option', None, 'gs.option.tests', 'bool_id')

    def testConvertToSchemaValue(self):
        self.assertEqual(type(self.option.converter.toSchemaValue('True')), bool)
        self.assertEqual(type(self.option.converter.toSchemaValue('False')), bool)
        
    def testConvertToStorageValue(self):
        self.assertEqual(type(self.option.converter.toStorageValue(True)), unicode)
        self.assertEqual(type(self.option.converter.toStorageValue(False)), unicode)

    def testFailValidation(self):
        self.assertRaises(WrongType, self.option.converter.toStorageValue, 1.0)
        self.assertRaises(WrongType, self.option.converter.toStorageValue, '1')
        self.assertRaises(WrongType, self.option.converter.toStorageValue, u'1')
        self.assertRaises(WrongType, self.option.converter.toStorageValue, [1,2,3])
        self.assertRaises(WrongType, self.option.converter.toStorageValue, (1,2,3))
        self.assertRaises(WrongType, self.option.converter.toStorageValue, {'1':2})
        
class FloatTest(BaseConverterTest):
    def _setupOption(self):
        self.option = createObject('groupserver.Option', None, 'gs.option.tests', 'float_id')
        
    def testConvertToSchemaValue(self):
        self.assertEqual(type(self.option.converter.toSchemaValue('1.0')), float)
        self.assertEqual(type(self.option.converter.toSchemaValue('1'*100+'.0')), float)
        
    def testConvertToStorageValue(self):
        self.assertEqual(type(self.option.converter.toStorageValue(1.0)), unicode)
        self.assertEqual(type(self.option.converter.toStorageValue(10.0**100)), unicode)

    def testFailValidation(self):
        self.assertRaises(WrongType, self.option.converter.toStorageValue, '1')
        self.assertRaises(WrongType, self.option.converter.toStorageValue, u'1')
        self.assertRaises(WrongType, self.option.converter.toStorageValue, [1,2,3])
        self.assertRaises(WrongType, self.option.converter.toStorageValue, (1,2,3))
        self.assertRaises(WrongType, self.option.converter.toStorageValue, {'1':2})

class TextTest(BaseConverterTest):
    def _setupOption(self):
        self.option = createObject('groupserver.Option', None, 'gs.option.tests', 'text_id')
                
    def testConvertToSchemaValue(self):
        self.assertEqual(type(self.option.converter.toSchemaValue(u'This is some text')), unicode)
        
    def testConvertToStorageValue(self):
        self.assertEqual(type(self.option.converter.toStorageValue(u'this is some text')), unicode)

    def testFailValidation(self):
        self.assertRaises(WrongType, self.option.converter.toStorageValue, 'non-unicode text')
        self.assertRaises(WrongType, self.option.converter.toStorageValue, True)
        self.assertRaises(WrongType, self.option.converter.toStorageValue, 1)
        self.assertRaises(WrongType, self.option.converter.toStorageValue, 1.0)
        self.assertRaises(WrongType, self.option.converter.toStorageValue, [1,2,3])
        self.assertRaises(WrongType, self.option.converter.toStorageValue, (1,2,3))
        self.assertRaises(WrongType, self.option.converter.toStorageValue, {'1':2})

def test_suite():
   suite = TestSuite()
   suite.addTest(makeSuite(ConverterTest))
   suite.addTest(makeSuite(BoolTest))
   suite.addTest(makeSuite(FloatTest))
   suite.addTest(makeSuite(IntTest))
   suite.addTest(makeSuite(TextTest))
   
   return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
