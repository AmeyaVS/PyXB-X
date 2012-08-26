# -*- coding: utf-8 -*-
import pyxb.binding.generate
import pyxb.binding.datatypes as xs
import pyxb.binding.basis
import pyxb.utils.domutils
import gc

import os.path
xsd='''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="instance">
    <xs:complexType>
      <xs:all>
         <xs:element name="inner" maxOccurs="unbounded">
           <xs:complexType>
             <xs:all>
               <xs:element name="text" type="xs:string"/>
               <xs:element name="number" type="xs:integer"/>
             </xs:all>
           </xs:complexType>
         </xs:element>
      </xs:all>
    </xs:complexType>
  </xs:element>
</xs:schema>
'''

#file('schema.xsd', 'w').write(xsd)
code = pyxb.binding.generate.GeneratePython(schema_text=xsd)
#file('code.py', 'w').write(code)
#print code

rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb.exceptions_ import *

import unittest

import os

class TestBug_200908271556(unittest.TestCase):
    # No, this isn't portable.  No, I don't care.
    __statm = file('/proc/%d/statm' % (os.getpid(),))

    def __getMem (self):
        self.__statm.seek(0)
        return int(self.__statm.read().split()[0])

    def testMemory (self):
        xmls = '<instance><inner><text>text</text><number>45</number></inner></instance>'
        base_at = 10
        check_at = 20
        growth_limit = 1.10
        iter = 0
        gc.collect()
        while True:
            iter += 1
            if base_at == iter:
                gc.collect()
                base_mem = self.__getMem()
            elif check_at == iter:
                gc.collect()
                check_mem = self.__getMem()
                growth = check_mem - base_mem
                self.assertTrue(0 == growth, 'growth %s' % (growth,))
                break
            instance = CreateFromDocument(xmls)
            xmls = instance.toxml("utf-8", root_only=True)

if __name__ == '__main__':
    import logging
    logging.basicConfig()
    unittest.main()
