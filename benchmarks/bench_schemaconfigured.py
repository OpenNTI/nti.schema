from __future__ import print_function, absolute_import
import pyperf

from zope.interface import Interface
from zope.interface import classImplements
from zope.interface import implementer
from zope.interface.interface import InterfaceClass

from nti.schema.field import Bool
from nti.schema.schema import SchemaConfigured
from nti.schema.fieldproperty import createFieldProperties

# The number of interfaces seems to directly relate to the speed, with more
# being much slower.
INTERFACE_COUNT = 20
INNERLOOPS = 100
# A bunch of interfaces, each declaring
# one field. No inheritance.
shallow_ifaces = [
    InterfaceClass(
        'I' + ('0' * 20) + str(i),
        (Interface,),
        {'field_' + str(i): Bool()}
    )
    for i in range(INTERFACE_COUNT)
]

def make_shallow_classes():
    classes = []
    for iface in shallow_ifaces:
        cls = type(
            'Class' + iface.__name__,
            (object,),
            {}
        )
        classImplements(cls, iface)
        classes.append(cls)
    return classes

shallow_classes = make_shallow_classes()

IWideInheritance = InterfaceClass(
    'IWideInheritance',
    tuple(shallow_ifaces),
    {'__doc__': "Inherits from unrelated interfaces"}
)

WideInheritance = type(
    'WideInheritance',
    tuple(shallow_classes),
    {'__doc__': "Inherits from unrelated classes"}
)

class SCWideInheritance(WideInheritance, SchemaConfigured):
    pass

@implementer(*shallow_ifaces)
class ShallowInheritance(object):
    """
    Implements each individual interface.
    """
    for iface in shallow_ifaces:
        createFieldProperties(iface)

class SCShallowInheritance(ShallowInheritance, SchemaConfigured):
    pass


def make_deep_ifaces():
    children = []
    base = Interface
    for i, iface in enumerate(shallow_ifaces):
        child = InterfaceClass(
            'IDerived' + base.__name__,
            (iface, base,),
            {'field_' + str(i): Bool()}
        )
        base = child
        children.append(child)
    return children

deep_ifaces = make_deep_ifaces()
# An interface that inherits from 99 other interfaces, each
# declaring a single field.
IDeepestInheritance = deep_ifaces[-1]

def make_deep_classes(extra_bases=()):
    classes = []
    base = extra_bases + (object,)
    for iface in deep_ifaces:
        cls = type(
            'Class' + iface.__name__,
            base,
            {}
        )
        classImplements(cls, iface)
        base = (cls,)
        classes.append(cls)

    return classes

deep_classes = make_deep_classes()

@implementer(IDeepestInheritance)
class DeepestInheritance(deep_classes[-1]):
    """
    A single class that implements an interface that's deeply inherited.

    Has field properties.
    """
    createFieldProperties(IDeepestInheritance)

sc_deep_classes = make_deep_classes((SchemaConfigured,))

@implementer(IDeepestInheritance)
class SCDeepestInheritance(sc_deep_classes[-1], SchemaConfigured):
    """
    Has field properties.
    """
    createFieldProperties(IDeepestInheritance)

def bench_create(loops, cls):
    t0 = pyperf.perf_counter()
    for _ in range(loops):
        for _ in range(INNERLOOPS):
            cls()
    return pyperf.perf_counter() - t0



runner = pyperf.Runner()

for bench_cls in (
        WideInheritance, # These have no field properties.
        SCWideInheritance,
        DeepestInheritance,
        SCDeepestInheritance,
        ShallowInheritance,
        SCShallowInheritance
):

    runner.bench_time_func(
        'Create ' + bench_cls.__name__,
        bench_create,
        bench_cls,
        inner_loops=INNERLOOPS
        )

#bench_create(10000, SCDeepestInheritance)
