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
    description             = 'GPU terrain generator',
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
            'style/*.hss',
            'style/images/*.png',
            'style/fonts/*.ttf',
            'shaders/*.frag',
            'shaders/*.vert',
            'shaders/lighting/*.frag',
            'shaders/lighting/*.vert',
        ]
    },
    packages                = ['lithosphere'],
    scripts                 = ['lithosphere/lithosphere'],
    install_requires        = ['setuptools', 'pyglet', 'halogen', 'gletools'],
    platforms               = ['any'],
    app                     = ['lithosphere/app.py'],
)
