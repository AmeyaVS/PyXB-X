import pywxsb.binding.generate
from xml.dom import minidom
from xml.dom import Node

import os.path
schema_path = '%s/../schemas/test-deconflict.xsd' % (os.path.dirname(__file__),)
code = pywxsb.binding.generate.GeneratePython(schema_file=schema_path)

rv = compile(code, 'test', 'exec')
eval(rv)

from pywxsb.exceptions_ import *

import unittest

class TestDeconflict (unittest.TestCase):
    def testAttributes (self):
        self.assertEqual(2, len(CTD_empty._ElementMap))
        ef = CTD_empty._ElementMap['CreateFromDOM']
        self.assertEqual('CreateFromDOM_', ef.pythonField())
        self.assertFalse(ef.isPlural())
        self.assertTrue(ef.defaultValue() is None)
        ef = CTD_empty._ElementMap['Factory']
        self.assertEqual('Factory_', ef.pythonField())
        self.assertFalse(ef.isPlural())
        self.assertTrue(ef.defaultValue() is None)
        self.assertEqual(2, len(CTD_empty._AttributeMap))
        self.assertEqual('toDOM_', CTD_empty._AttributeMap['toDOM'].pythonField())
        self.assertEqual('Factory__', CTD_empty._AttributeMap['Factory'].pythonField())

if __name__ == '__main__':
    unittest.main()
    