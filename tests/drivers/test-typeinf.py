# -*- coding: utf-8 -*-
import pyxb
import pyxb.binding.generate
import pyxb.utils.domutils

from xml.dom import Node

import os.path
schema_path = '%s/../schemas/test-typeinf.xsd' % (os.path.dirname(__file__),)
code = pyxb.binding.generate.GeneratePython(schema_location=schema_path)

rv = compile(code, 'test', 'exec')
eval(rv)

import unittest

class TestTypeInference (unittest.TestCase):
    def testBasic (self):
        e = anyType(4) # should be int
        self.assertEqual(e.int, 4)
        self.assertTrue(e.float is None)
        self.assertTrue(e.str is None)
        e = anyType(4.4)
        self.assertTrue(e.int is None)
        self.assertEqual(e.float, 4.4)
        self.assertTrue(e.str is None)
        e = anyType("3")
        self.assertTrue(e.int is None)
        self.assertTrue(e.float is None)
        self.assertEqual(e.str, "3")

if __name__ == '__main__':
    import logging
    logging.basicConfig()
    unittest.main()
    
        
