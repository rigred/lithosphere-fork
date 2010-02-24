# -*- coding: utf-8 -*-

"""
    lithosphere
    ~~~~~~~~~~~

    A GPU terrain generator

    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
    
from setuptools import setup

setup(
    name                    = 'lithosphere',
    version                 = '0.1.0', 
    description             = 'OpenGL GUI Toolkit',
    long_description        = __doc__,
    license                 = 'GNU AFFERO GENERAL PUBLIC LICENSE (AGPL) Version 3',
    url                     = 'http://hg.codeflow.org/lithosphere',
    download_url            = 'http://hg.codeflow.org/',
    author                  = 'Florian Boesch',
    author_email            = 'pyalot@gmail.com',
    maintainer              = 'Florian Boesch',
    maintainer_email        = 'pyalot@gmail.com',
    zip_safe                = False,
    include_package_data    = True,
    package_data            = {
        'lithosphere':[
            'style/*.css',
            'style/images/*.png',
            'style/fonts/*.ttf',
            'shaders/*.frag*',
            'shaders/lighting/*.frag*',
        ]
    },
    packages                = ['lithosphere'],
    scripts                 = ['lithosphere/lithosphere'],
    install_requires        = ['setuptools', 'pyglet', 'halogen', 'gletools', 'UniversalDialogs'],
    platforms               = ['any'],
)
