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
"""Functional Tests for Interface Documentation Module.

$Id: ftests.py,v 1.1 2004/03/28 23:40:52 srichter Exp $
"""
import unittest
from zope.testing.functional import BrowserTestCase

class InterfaceModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    def testMenu(self):
        response = self.publish(
            '/++apidoc++/Interface/menu.html', 
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find(
            'zope.app.apidoc.ifacemodule.IInterfaceModule') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Interface/menu.html',
                                 basic='mgr:mgrpw')

    def testInterfaceDetailsView(self):
        response = self.publish(
            '/++apidoc++/Interface'
            '/zope.app.apidoc.ifacemodule.IInterfaceModule'
            '/apiindex.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Interface API Documentation Module') > 0)
        self.checkForBrokenLinks(
            body,
            '/++apidoc++/Interface'
            '/zope.app.apidoc.ifacemodule.IInterfaceModule'
            '/apiindex.html',            
            basic='mgr:mgrpw')
        
    

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(InterfaceModuleTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')