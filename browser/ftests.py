##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Functional Tests for API Documentation.

$Id: ftests.py,v 1.1 2004/03/28 23:39:16 srichter Exp $
"""
import unittest
from zope.testing.functional import BrowserTestCase

class APIDocTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    def testMenu(self):
        response = self.publish('/++apidoc++/menu.html', 
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Click on one of the Documentation Modules') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/menu.html',
                                 basic='mgr:mgrpw')


    def testIndexView(self):
        response = self.publish('/++apidoc++/index.html', 
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Zope 3 API Docs') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/index.html',
                                 basic='mgr:mgrpw')

    def testContentsView(self):
        response = self.publish('/++apidoc++/contents.html', 
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('<h1>Zope 3 API Documentation</h1>') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/contents.html',
                                 basic='mgr:mgrpw')

    def testModuleListView(self):
        response = self.publish('/++apidoc++/modulelist.html',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find(
            '<div class="apihead">Zope 3 API Docs</div>') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/modulelist.html',
                                 basic='mgr:mgrpw')
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(APIDocTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')