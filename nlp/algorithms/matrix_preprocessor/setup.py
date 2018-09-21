#!/usr/bin/env python3

import os
import platform

import numpy
from distutils.core import setup
from Cython.Distutils import build_ext
from distutils.extension import Extension

# do a platform check
#thisPlatform = du.get_platform()

# extra_ccflags = ''
# this_os = platform.system()
# if 'Darwin' == this_os:
#     extra_ccflags = '-mmacosx-version-min=10.7'

# Path to the .hpp interface file
hpp_path = 'include'

# Path to archive file (.a file)
archive_path = os.path.join('build', 'bin')
archive_filename = 'libpreprocess.a'
archive_file_path = os.path.join(archive_path, archive_filename)

# extension module section
ext_modules = [Extension(
    name='matrix_preprocessor',
    sources=['interface/matrix_preprocessor.pyx'],
    include_dirs = ['include', numpy.get_include()],
    libraries=['m'],
    library_dirs=[archive_path],
    extra_objects=[archive_file_path],
    language='c++',
    extra_compile_args=[
        '-std=c++11',
        '-fpermissive',
        '--stdlib=libc++',
    #    extra_ccflags
    ],
    extra_link_args=['--stdlib=libc++'])
]

# call the main setup code from distutils
setup(
    name = 'matrix_preprocessor',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules,
    version = 0.1
)

