here=`pwd`

cd ../../../gletools
python setup.py bdist_egg
cp dist/gletools-0.1.0-py2.6.egg $here
cd $here

cd ../../../halogen
python setup.py bdist_egg
cp dist/halogen-0.1.0-py2.6.egg $here
cd $here

cd ../../../pyglet
python setup.py bdist_egg
cp dist/pyglet-1.2dev-py2.6.egg $here
cd $here

cd ../..
python setup.py bdist_egg
cp dist/lithosphere-0.1.0-py2.6.egg $here
cd $here
