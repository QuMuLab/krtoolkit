#!/usr/bin/env python

from distutils.core import setup

setup(name = 'KR Toolkit',
      version = '0.1',
      description = 'Utilities for common Knowledge Representation and Reasoning Tasks',
      author = 'Christian Muise',
      author_email = 'christian.muise@gmail.com',
      url = 'http://code.google.com/p/krtoolkit/',
      packages = ['krrt',
                'krrt.sat',
                'krrt.stats',
                'krrt.utils',
                'krrt.planning',
                'krrt.planning.pddl',
                'krrt.planning.sas',
                'krrt.planning.strips',
                'krrt.search',
                'krrt.search.backtrack',
                'krrt.search.localsearch',
                'krrt.search.backtrack.viz',
                'krrt.search.localsearch.viz'
                ],
     )

