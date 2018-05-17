#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Sun May 10 01:31:47 2015
# ht <515563130@qq.com, weixin:jacoolee>
import os

try:
    from setuptools import setup
except ImportError:
    pass


useless_files = "build dist" # blackpearl.egg-info"
print "removing non-sense files: %s [%s]" % ( useless_files, 'OK' if 0 == os.system( 'rm -rf %s' % useless_files ) else 'FAILED' )

setup (
    name = 'blackpearl',
    version = 0.92,
    keywords = ('web front end server'),
    description = '',
    author = 'jacoolee (515563130@qq.com)',
    packages = [ 'blackpearl' ],
)

print "removing non-sense files: %s [%s]" % ( useless_files, 'OK' if 0 == os.system( 'rm -rf %s' % useless_files ) else 'FAILED' )

print "blackpearl successfully installed, well done"
