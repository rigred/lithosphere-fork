#!/usr/bin/env python

if __name__ == '__main__':
    import os, sys
    here = os.path.dirname(os.path.abspath(__file__))
    for name in os.listdir(here):
        if name.endswith('.egg'):
            sys.path.insert(0, os.path.join(here, name))

    from lithosphere.main import main
    main()
