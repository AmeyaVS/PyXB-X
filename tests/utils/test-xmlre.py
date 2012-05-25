# -*- coding: utf-8 -*-
import pyxb.utils.xmlre as xmlre
import pyxb.utils.unicode as unicode
import re

import unittest

class TestXMLRE (unittest.TestCase):
    def assertMatches(self, xml_pattern, value):
        '''Helper function to assert a value matches an XSD regexp pattern.'''
        py_pattern = xmlre.XMLToPython(xml_pattern)
        compiled = re.compile(py_pattern)
        mo = compiled.match(value)
        self.assertIsNotNone(mo, 'XML pattern %r compiles to Python pattern '
                             '%r which doesn\'t match value %r but should'
                             % (xml_pattern, py_pattern, value))

    def assertNoMatch(self, xml_pattern, value):
        '''Helper function to assert a value does not matche an XSD regexp
        pattern.'''
        py_pattern = xmlre.XMLToPython(xml_pattern)
        compiled = re.compile(py_pattern)
        mo = compiled.match(value)
        self.assertIsNone(mo, 'XML pattern %r compiles to Python pattern '
                          '%r which matches value %r but shouldn\'t'
                          % (xml_pattern, py_pattern, value))

    def testRangeErrors (self):
        self.assertTrue(xmlre.MaybeMatchCharacterClass('', 1) is None)

    def testWildcardEscape (self):
        (charset, position) = xmlre.MaybeMatchCharacterClass('.', 0)
        self.assertEqual(charset, unicode.WildcardEsc)
        self.assertEqual(position, 1)

    def testSingleCharEscapes (self):
        # 17 chars recognized as escapes
        self.assertEqual(len(unicode.SingleCharEsc), 17)

        (charset, position) = xmlre.MaybeMatchCharacterClass(r'\t', 0)
        self.assertEqual(charset.asTuples(), [ (9, 9) ])
        self.assertEqual(2, position)

        (charset, position) = xmlre.MaybeMatchCharacterClass(r'\?', 0)
        self.assertEqual(charset.asTuples(), [ (ord('?'), ord('?')) ])
        self.assertEqual(2, position)

        (charset, position) = xmlre.MaybeMatchCharacterClass(r'\\', 0)
        self.assertEqual(charset.asTuples(), [ (ord('\\'), ord('\\')) ])
        self.assertEqual(2, position)

    def testMultiCharEscapes (self):
        # 5*2 chars recognized as escapes
        self.assertEqual(len(unicode.MultiCharEsc), 10)
        (charset, position) = xmlre.MaybeMatchCharacterClass(r'\s', 0)
        self.assertEqual(charset.asTuples(), [ (9, 10), (13, 13), (32, 32) ])
        self.assertEqual(2, position)

    def testMatchCharProperty (self):
        self.assertRaises(xmlre.RegularExpressionError, xmlre._MatchCharPropBraced, "L", 0)
        self.assertRaises(xmlre.RegularExpressionError, xmlre._MatchCharPropBraced, "{L", 0)
        text = "{L}"
        (charset, position) = xmlre._MatchCharPropBraced(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset, unicode.PropertyMap['L'])
        text = "{IsCyrillic}"
        (charset, position) = xmlre._MatchCharPropBraced(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset, unicode.BlockMap['Cyrillic'])

    def testCharProperty (self):
        text = r'\p{D}'
        self.assertRaises(xmlre.RegularExpressionError, xmlre.MaybeMatchCharacterClass, text, 0)
        text = r'\P{D}'
        self.assertRaises(xmlre.RegularExpressionError, xmlre.MaybeMatchCharacterClass, text, 0)
        text = r'\p{N}'
        (charset, position) = xmlre.MaybeMatchCharacterClass(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset, unicode.PropertyMap['N'])
        text = r'\P{N}'
        (charset, position) = xmlre.MaybeMatchCharacterClass(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset.negate(), unicode.PropertyMap['N'])
        text = r'\p{Sm}'
        (charset, position) = xmlre.MaybeMatchCharacterClass(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset, unicode.PropertyMap['Sm'])

        text = r'\p{IsArrows}'
        (charset, position) = xmlre.MaybeMatchCharacterClass(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset, unicode.BlockMap['Arrows'])
        text = r'\P{IsArrows}'
        (charset, position) = xmlre.MaybeMatchCharacterClass(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset.negate(), unicode.BlockMap['Arrows'])

    def testCharGroup (self):
        self.assertRaises(xmlre.RegularExpressionError, xmlre.MaybeMatchCharacterClass, '[]', 0)
        self.assertRaises(xmlre.RegularExpressionError, xmlre.MaybeMatchCharacterClass, '[A-]', 0)
        self.assertRaises(xmlre.RegularExpressionError, xmlre.MaybeMatchCharacterClass, '[A-]', 0)
        text = r'[A-Z]'
        #(charset, position) = xmlre.MaybeMatchCharacterClass(text, 0)
        #self.assertEqual(position, len(text))
        #self.assertEqual(charset, unicode.CodePointSet((ord('A'), ord('Z'))))

    def testCharOrSCE (self):
        self.assertRaises(xmlre.RegularExpressionError, xmlre._CharOrSCE, '[', 0)
        self.assertRaises(xmlre.RegularExpressionError, xmlre._CharOrSCE, ']', 0)
        self.assertRaises(xmlre.RegularExpressionError, xmlre._CharOrSCE, '-', 0)
        (charset, position) = xmlre._CharOrSCE('A', 0)
        self.assertEqual(1, position)
        self.assertEqual(charset, 'A')
        (charset, position) = xmlre._CharOrSCE(r'\t', 0)
        self.assertEqual(2, position)
        self.assertEqual("\t", charset)
        (charset, position) = xmlre._CharOrSCE(u'\u0041', 0)
        self.assertEqual(1, position)
        self.assertEqual("A", charset)

    def testMatchPosCharGroup (self):
        text = 'A'
        (charset, position) = xmlre._MatchPosCharGroup(text, 0)
        self.assertEqual(position, 1)
        self.assertEqual(charset, unicode.CodePointSet(ord('A')))
        text = r'\n'
        (charset, position) = xmlre._MatchPosCharGroup(text, 0)
        self.assertEqual(position, 2)
        self.assertEqual(charset, unicode.CodePointSet(10))
        text = r'-'
        (charset, position) = xmlre._MatchPosCharGroup(text, 0)
        self.assertEqual(position, 1)
        self.assertEqual(charset, unicode.CodePointSet(ord('-')))
        text = 'A-Z'
        (charset, position) = xmlre._MatchPosCharGroup(text, 0)
        self.assertEqual(position, 3)
        self.assertEqual(charset, unicode.CodePointSet((ord('A'), ord('Z'))))
        text = r'\t-\r'
        (charset, position) = xmlre._MatchPosCharGroup(text, 0)
        self.assertEqual(position, 5)
        self.assertEqual(charset, unicode.CodePointSet((9, 13)))
        text = r'\t-A'
        (charset, position) = xmlre._MatchPosCharGroup(text, 0)
        self.assertEqual(position, 4)
        self.assertEqual(charset, unicode.CodePointSet((9, ord('A'))))
        text = r'Z-\]'
        (charset, position) = xmlre._MatchPosCharGroup(text, 0)
        self.assertEqual(position, 4)
        self.assertEqual(charset, unicode.CodePointSet((ord('Z'), ord(']'))))
        text = 'Z-A'
        self.assertRaises(xmlre.RegularExpressionError, xmlre._MatchPosCharGroup, text, 0)
        
    def testMatchCharClassExpr (self):
        self.assertRaises(xmlre.RegularExpressionError, xmlre._MatchCharClassExpr, 'missing open', 0)
        self.assertRaises(xmlre.RegularExpressionError, xmlre._MatchCharClassExpr, '[missing close', 0)
        first_five = unicode.CodePointSet( (ord('A'), ord('E')) )
        text = r'[ABCDE]'
        (charset, position) = xmlre._MatchCharClassExpr(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset, first_five)
        text = r'[^ABCDE]'
        (charset, position) = xmlre._MatchCharClassExpr(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset.negate(), first_five)
        text = r'[A-Z-[GHI]]'
        expected = unicode.CodePointSet( (ord('A'), ord('Z')) )
        expected.subtract( (ord('G'), ord('I') ))
        (charset, position) = xmlre._MatchCharClassExpr(text, 0)
        self.assertEqual(position, len(text))
        self.assertEqual(charset, expected)
        text = r'[\p{L}-\p{Lo}]'
        self.assertRaises(xmlre.RegularExpressionError, xmlre._MatchCharClassExpr, text, 0)
        text = r'[\p{L}-[\p{Lo}]]'
        (charset, position) = xmlre._MatchCharClassExpr(text, 0)
        expected = unicode.CodePointSet(unicode.PropertyMap['L'])
        expected.subtract(unicode.PropertyMap['Lo'])
        self.assertEqual(position, len(text))
        self.assertEqual(charset, expected)
        
    def testXMLToPython (self):
        self.assertEqual(r'^123$', xmlre.XMLToPython('123'))
        # Note that single-char escapes in the expression are
        # converted to character classes.
        self.assertEqual(r'^Why[ ]not[?]$', xmlre.XMLToPython(r'Why[ ]not\?'))

    def testRegularExpressions (self):
        text = u'[\i-[:]][\c-[:]]*'
        compiled_re = re.compile(xmlre.XMLToPython(text))
        self.assertTrue(compiled_re.match('identifier'))
        self.assertFalse(compiled_re.match('0bad'))
        self.assertFalse(compiled_re.match(' spaceBad'))
        self.assertFalse(compiled_re.match('qname:bad'))
        text = u'\\i\\c*'
        text_py = xmlre.XMLToPython(text)
        compiled_re = re.compile(text_py)
        self.assertTrue(compiled_re.match('identifier'))
        self.assertTrue(compiled_re.match('_underscore'))

    def testCnUnicodeClass(self):
        # The Cn class is basically "everything that is not included in the
        # Unicode character database".  So it requires special handling when
        # you parse the Unicode character database.  It is really easy to
        # miss this and leave the Cn class empty.
        self.assertNoMatch(u"foo\\p{Cn}bar", u"fooWbar")
        self.assertMatches(u"foo\\p{Cn}bar", u"foo\ufffebar")
        self.assertMatches(u"foo\\P{Cn}bar", u"fooWbar")
        self.assertNoMatch(u"foo\\P{Cn}bar", u"foo\ufffebar")

    def testCnUnicodeClassInC(self):
        # If the Cn class is wrong (see above), then C will probably be wrong
        # too.
        self.assertNoMatch(u"foo\\p{C}bar", u"fooWbar")
        self.assertMatches(u"foo\\p{C}bar", u"foo\ufffebar")
        self.assertMatches(u"foo\\P{C}bar", u"fooWbar")
        self.assertNoMatch(u"foo\\P{C}bar", u"foo\ufffebar")

if __name__ == '__main__':
    unittest.main()
