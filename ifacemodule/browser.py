##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Interface Details View

$Id$
"""
from types import FunctionType, MethodType, ClassType, TypeType
from zope.component import ComponentLookupError
from zope.interface.declarations import providedBy
from zope.interface.interfaces import IMethod, IInterface 
from zope.proxy import removeAllProxies
from zope.schema.interfaces import IField

from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.apidoc.utilities import getPythonPath, stx2html
from zope.app.apidoc.classmodule import classRegistry

def _get(iface, type):
    """Return a dictionary containing all the attributes in an interface.

    The type specifies whether we are looking for attributes or methods.

    Example::

      >>> from zope.interface import Interface, Attribute
      >>> from zope.schema import Field

      >>> class IFoo(Interface):
      ...     foo = Field()
      ...     bar = Field()
      ...     def blah():
      ...         pass

      >>> _get(IFoo, IMethod).keys()
      ['blah']

      >>> names = _get(IFoo, IField).keys()
      >>> names.sort()
      >>> names
      ['bar', 'foo']
    """
    iface = removeAllProxies(iface)
    items = {}
    for name in iface:
        attr = iface[name]
        if type.providedBy(attr):
            items[name] = attr
    return items


def _getInOrder(iface, type,
                _itemsorter=lambda x, y: cmp(x[1].order, y[1].order)):
    """Return a list of (name, value) tuples in native interface order.

    The type specifies whether we are looking for attributes or methods. The
    '_itemsorter' argument provides the function that is used to order the
    fields. The default function should be the correct one for 99% of your
    needs.

    Example::

      >>> from zope.interface import Interface, Attribute
      >>> from zope.schema import Field

      >>> class IFoo(Interface):
      ...     foo = Field()
      ...     bar = Field()
      ...     def blah():
      ...         pass

      >>> [n for n, a in _getInOrder(IFoo, IMethod)]
      ['blah']

      >>> [n for n, a in _getInOrder(IFoo, IField)]
      ['foo', 'bar']
    """
    items = _get(iface, type).items()
    items.sort(_itemsorter)
    return items


def _getFieldInterface(field):
    """Return PT-friendly dict about the field's interface.

    Examples::

      >>> from zope.app.apidoc.tests import pprint
      >>> from zope.interface import implements, Interface
      
      >>> class IField(Interface):
      ...     pass
      >>> class ISpecialField(IField):
      ...     pass
      >>> class Field:
      ...     implements(IField)
      >>> class SpecialField:
      ...     implements(ISpecialField)
      >>> class ExtraField(SpecialField):
      ...     pass

      >>> info = _getFieldInterface(Field())
      >>> pprint(info)
      [('id', 'zope.app.apidoc.ifacemodule.browser.IField'),
       ('name', 'IField')]

      >>> info = _getFieldInterface(SpecialField())
      >>> pprint(info)
      [('id', 'zope.app.apidoc.ifacemodule.browser.ISpecialField'),
       ('name', 'ISpecialField')]

      >>> info = _getFieldInterface(ExtraField())
      >>> pprint(info)
      [('id', 'zope.app.apidoc.ifacemodule.browser.ISpecialField'),
       ('name', 'ISpecialField')]
    """
    field = removeAllProxies(field)
    # This is bad, but due to bootstrapping, directlyProvidedBy does
    # not work 
    name = field.__class__.__name__
    ifaces = list(providedBy(field))
    # Usually fields have interfaces with the same name (with an 'I')
    for iface in ifaces:
        if iface.getName() == 'I' + name:
            return {'name': iface.getName(), 'id': getPythonPath(iface)}
    # Giving up...
    return {'name': ifaces[0].getName(), 'id': getPythonPath(ifaces[0])}


def _getRequired(field):
    """Return a string representation of whether the field is required.

    Examples::

      >>> class Field:
      ...     required = False

      >>> field = Field()
      >>> _getRequired(field)
      u'optional'
      >>> field.required = True
      >>> _getRequired(field)
      u'required'

    """
    if field.required:
        return _('required')
    else:
        return _('optional')


def _getRealFactory(factory):
    """Get the real factory.

    Sometimes the original factory is masked by functions. If the function
    keeps track of the original factory, use it.
    """
    if isinstance(factory, FunctionType) and hasattr(factory, 'factory'):
        return factory.factory
    return factory


class InterfaceDetails(object):
    """View class for an Interface."""

    def getId(self):
        """Return the id of the field as it is defined for the interface
        utility.

        Example::

          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()
          >>> details.getId()
          'IFoo'
        """
        return zapi.name(self.context)

    def getDoc(self):
        """Return the main documentation string of the interface.

        Example::

          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()
          >>> details.getDoc()[:34]
          '<h1>This is the Foo interface</h1>'
        """
        return stx2html(self.context.__doc__)

    def getBases(self):
        """Get all bases of this class

        Example::

          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()
          >>> details.getBases()
          ['zope.interface.Interface']
        """
        return [getPythonPath(base) for base in self.context.__bases__]

    def getTypes(self):
        """Return a list of interface types that are specified for this
        interface.

        Note that you should only expect one type at a time.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> from zope.interface import Interface, directlyProvides
          >>> class IType(Interface):
          ...     pass

          >>> details = getInterfaceDetails()
          >>> details.getTypes()
          []

          >>> directlyProvides(removeAllProxies(details.context), IType)
          >>> type = details.getTypes()[0]
          >>> pprint(type)
          [('name', 'IType'),
           ('path', 'zope.app.apidoc.ifacemodule.browser.IType')]

          Cleanup

          >>> directlyProvides(removeAllProxies(details.context), [])
        """
        context = removeAllProxies(self.context)
        types = list(providedBy(context))
        types.remove(IInterface)
        return [{'name': type.getName(),
                 'path': getPythonPath(type)}
                for type in types]
    
    def getAttributes(self):
        r"""Return a list of attributes in the order they were specified.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> attrs = details.getAttributes()
          >>> pprint(attrs)
          [[('doc', '<p>This is bar.</p>\n'), ('name', 'bar')],
           [('doc', '<p>This is foo.</p>\n'), ('name', 'foo')]]
        """
        iface = removeAllProxies(self.context)
        attrs = []
        for name in iface:
            attr = iface[name]
            if not IMethod.providedBy(attr) and not IField.providedBy(attr):
                attrs.append(attr)
        return [{'name': attr.getName(),
                 'doc': stx2html(attr.getDoc() or '', 3)}
                for attr in attrs]

    def getMethods(self):
        r"""Return a list of methods in the order they were specified.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> methods = details.getMethods()
          >>> pprint(methods)
          [[('doc', '<p>This is blah.</p>\n'),
            ('name', 'blah'),
            ('signature', '()')],
           [('doc', '<p>This is get.</p>\n'),
            ('name', 'get'),
            ('signature', '(key, default=None)')]]
        """        
        return [{'name': method.getName(),
                 'signature': method.getSignatureString(),
                 'doc': stx2html(method.getDoc() or '', 3)}
                for method in _get(self.context, IMethod).values()]
            
    def getFields(self):
        """Return a list of fields in the order they were specified.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> fields = details.getFields()
          >>> pprint(fields)
          [[('default', "u'Foo'"),
            ('description', u'Title'),
            ('iface',
             [('id', 'zope.schema.interfaces.ITextLine'),
              ('name', 'ITextLine')]),
            ('name', 'title'),
            ('required', u'required')],
           [('default', "u'Foo.'"),
            ('description', u'Desc'),
            ('iface',
             [('id', 'zope.schema.interfaces.IText'), ('name', 'IText')]),
            ('name', 'description'),
            ('required', u'optional')]]
        """
        fields = map(lambda x: x[1], _getInOrder(self.context, IField))
        return [{'name': field.getName(),
                 'iface': _getFieldInterface(field),
                 'required': _getRequired(field),
                 'default': field.default.__repr__(),
                 'description': field.description
                 }
                for field in fields]

    def getRequiredAdapters(self):
        """Get adapters where this interface is required.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> adapters = details.getRequiredAdapters()
          >>> adapters.sort()
          >>> pprint(adapters)
          [[('factory', 'None.append'),
            ('factory_url', 'None/append'),
            ('name', None),
            ('provided', None),
            ('required', [])],
           [('factory',
             'zope.app.location.traversing.LocationPhysicallyLocatable'),
            ('factory_url',
             'zope/app/location/traversing/LocationPhysicallyLocatable'),
            ('name', ''),
            ('provided',
             'zope.app.traversing.interfaces.IPhysicallyLocatable'),
            ('required', [])]]
        """
        service = zapi.getService('Adapters')
        iface = removeAllProxies(self.context)
        adapters = []
        for reg in service.registrations():
            # Only grab the adapters for which this interface is required
            if reg.required and reg.required[0] is not None and iface not in reg.required:
                continue
            factory = _getRealFactory(reg.value)
            path = getPythonPath(factory)
            if type(factory) in (FunctionType, MethodType):
               url = None
            else:
                url = path.replace('.', '/')
            adapters.append({
                'provided': getPythonPath(reg.provided),
                'required': [getPythonPath(iface)
                             for iface in reg.required
                             if iface is not None],
                'name': getattr(reg, 'name', None),
                'factory': path,
                'factory_url': url
                })
        return adapters
        
    def getProvidedAdapters(self):
        """Get adapters where this interface is provided.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> adapters = details.getProvidedAdapters()
          >>> pprint(adapters)
          [[('factory', '__builtin__.object'),
            ('factory_url', '__builtin__/object'),
            ('name', ''),
            ('required', ['zope.app.apidoc.ifacemodule.tests.IBar'])]]
        """
        service = zapi.getService('Adapters')
        iface = removeAllProxies(self.context)
        adapters = []
        for reg in service.registrations():
            # Only grab adapters for which this interface is provided
            if iface is not reg.provided:
                continue
            factory = _getRealFactory(reg.value)
            path = getPythonPath(factory)
            if type(factory) in (FunctionType, MethodType):
               url = None
            else:
                url = path.replace('.', '/')
            adapters.append({
                'required': [getPythonPath(iface) for iface in reg.required],
                'name': reg.name,
                'factory': path,
                'factory_url': url
                })
        return adapters

    def getClasses(self):
        """Get the classes that implement this interface.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> classes = details.getClasses()
          >>> pprint(classes)
          [[('path', 'zope.app.apidoc.ifacemodule.tests.Foo'),
            ('url', 'zope/app/apidoc/ifacemodule/tests/Foo')]]
        """
        iface = removeAllProxies(self.context)
        classes = classRegistry.getClassesThatImplement(iface)
        return [{'path': path, 'url': path.replace('.', '/')}
                for path, klass in classes]

    def getFactories(self):
        """Return the factories, who will provide objects implementing this
        interface.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> factories = details.getFactories()
          >>> factories = [f.items() for f in factories]
          >>> factories = [f for f in factories if f.sort() is None]
          >>> factories.sort()
          >>> pprint(factories)
          [[('name', u'FooFactory'),
            ('title', 'Foo Factory'),
            ('url', 'zope/component/factory/Factory')]]
        """
        iface = removeAllProxies(self.context)
        factories = [(n, f) for n, f in
                    zapi.getFactoriesFor(iface)
                    if iface in tuple(f.getInterfaces())]
        info = []
        for name, factory in factories:
            if type(factory) in (ClassType, TypeType):
                klass = factory
            else:
                klass = factory.__class__
            path = getPythonPath(klass)
            info.append({'name': name or '<i>no name</i>',
                         'title': getattr(factory, 'title', ''),
                         'url': path.replace('.', '/')})
        return info

    def getUtilitiesFor(self):
        """Return all utilities that provide this interface.

        Example::

          >>> from zope.app.apidoc.tests import pprint
          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()

          >>> utils = details.getUtilitiesFor()
          >>> pprint(utils)
          [[('name', u'The Foo'),
            ('path', 'zope.app.apidoc.ifacemodule.tests.Foo'),
            ('url', 'zope/app/apidoc/ifacemodule/tests/Foo'),
            ('url_name', u'The Foo')]]
        """
        service = zapi.getService('Utilities')
        utils = service.getUtilitiesFor(removeAllProxies(self.context))
        info = []
        for name, util in utils:
            if type(util) in (ClassType, TypeType):
                klass = util
            else:
                klass = util.__class__
            path = getPythonPath(klass)
            info.append({'name': name or '<i>no name</i>',
                         'url_name': name or '__noname__',
                         'path': path,
                         'url': path.replace('.', '/')})
        return info

    def getServices(self):
        """Return all services (at most one)  that provide this interface.

        Example::

          >>> from tests import getInterfaceDetails
          >>> details = getInterfaceDetails()
          >>> details.getServices()
          ['Foo']
        """
        iface = removeAllProxies(self.context)
        service = zapi.getService('Services')
        services = service.getServiceDefinitions()
        return [ser[0] for ser in services if ser[1] is iface]
