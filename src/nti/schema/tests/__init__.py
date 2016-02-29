#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

try:
	# canonical location, not necessarily public yet
	from nti.testing.layers import ZopeComponentLayer
	from nti.testing.layers import ConfiguringLayerMixin
except ImportError:
	# knock off versions that work but lack flexibility
	import gc
	import os

	from zope import component

	from zope.component import eventtesting
	from zope.component.hooks import setHooks

	from zope.configuration import config
	from zope.configuration import xmlconfig

	from zope.dottedname import resolve as dottedname

	import zope.testing.cleanup

	import transaction

	class SharedCleanupLayer(object):

		@classmethod
		def setUp(cls):
			# You MUST implement this, otherwise zope.testrunner
			# will call the super-class again
			zope.testing.cleanup.cleanUp()

		@classmethod
		def tearDown(cls):
			# You MUST implement this, otherwise zope.testrunner
			# will call the super-class again
			zope.testing.cleanup.cleanUp()

		@classmethod
		def testSetUp(cls):
			pass

		@classmethod
		def testTearDown(cls):
			pass

	class ZopeComponentLayer(SharedCleanupLayer):

		@classmethod
		def setUp(cls):
			setHooks()  # zope.component.hooks registers a zope.testing.cleanup to reset these

		@classmethod
		def tearDown(cls):
			# always safe to clear events
			eventtesting.clearEvents()  # redundant with zope.testing.cleanup
			# resetHooks()  we never actually want to do this, it's not needed and can mess up other fixtures

		@classmethod
		def testSetUp(cls):
			setHooks()  # ensure these are still here; cheap and easy

		@classmethod
		def testTearDown(cls):
			# Some tear down needs to happen always
			eventtesting.clearEvents()
			transaction.abort()  # see comments above

	def _configure(self=None,
				   set_up_packages=(),
				   features=('devmode', 'testmode'),
				   context=None,
				   package=None):

		if features is not None:
			features = set(features)
		else:
			features = set()

		# This is normally created by a slug, but tests may not always
		# load the slug
		if os.getenv('DATASERVER_DIR_IS_BUILDOUT'):
			features.add('in-buildout')

		# zope.component.globalregistry conveniently adds
		# a zope.testing.cleanup.CleanUp to reset the globalSiteManager
		if context is None and (features or package):
			context = config.ConfigurationMachine()
			context.package = package
			xmlconfig.registerCommonDirectives(context)

		for feature in features:
			context.provideFeature(feature)

		if set_up_packages:

			logger.debug("Configuring %s with features %s", set_up_packages, features)

			for i in set_up_packages:
				__traceback_info__ = (i, self)
				if isinstance(i, tuple):
					filename = i[0]
					package = i[1]
				else:
					filename = 'configure.zcml'
					package = i

				if isinstance(package, basestring):
					package = dottedname.resolve(package)

				try:
					context = xmlconfig.file(filename, package=package, context=context)
				except IOError as e:
					# Did we pass in a test module (__name__) and there is no
					# configuration in that package? In that case, we want to
					# configure the parent package for sure
					module_path = getattr(package, '__file__', None)
					if (module_path
						and 'tests' in module_path
						and os.path.join(os.path.dirname(module_path), filename) == e.filename):
						parent_package_name = '.'.join(package.__name__.split('.')[:-2])
						package = dottedname.resolve(parent_package_name)
						context = xmlconfig.file(filename, package=package, context=context)
					else:
						raise

		return context

	class ConfiguringLayerMixin(object):

		set_up_packages = ()
		features = ('devmode', 'testmode')
		configuration_context = None

		@classmethod
		def setUp(cls):
			# You MUST implement this, otherwise zope.testrunner
			# will call the super-class again
			pass

		@classmethod
		def tearDown(cls):
			# You MUST implement this, otherwise zope.testrunner
			# will call the super-class again
			pass

		@classmethod
		def testSetUp(cls):
			pass

		@classmethod
		def testTearDown(cls):
			# Must implement
			pass

		@classmethod
		def setUpPackages(cls):
			gc.collect()
			cls.configuration_context = cls.configure_packages(set_up_packages=cls.set_up_packages,
															   features=cls.features,
															   context=cls.configuration_context)
			component.provideHandler(eventtesting.events.append, (None,))
			gc.collect()

		@classmethod
		def configure_packages(cls, set_up_packages=(), features=(), context=None):
			cls.configuration_context = _configure(self=cls,
												   set_up_packages=set_up_packages,
												   features=features,
												   context=context or cls.configuration_context)
			return cls.configuration_context

		@classmethod
		def tearDownPackages(cls):
			# This is a duplicate of zope.component.globalregistry
			gc.collect()
			component.getGlobalSiteManager().__init__('base')

			gc.collect()
			cls.configuration_context = None
