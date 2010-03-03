# -*- coding: utf-8 -*-

"""
    :copyright: 2010 by Florian Boesch <pyalot@gmail.com>.
    :license: GNU AGPL v3 or later, see LICENSE for more details.
"""
try:
    from json import *
except ImportError:
    try:
        from simplejson import *
    except ImportError:
        from cjson import *
