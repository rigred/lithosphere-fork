here=`pwd`
rm lithosphere.tgz
rm lithosphere.zip
mkdir lithosphere

cd ../../gletools
rm dist/*.egg
python setup.py bdist_egg
cp dist/gletools*.egg $here/lithosphere
cd $here

cd ../../halogen
rm dist/*.egg
python setup.py bdist_egg
cp dist/halogen*.egg $here/lithosphere
cd $here

cd ../../pyglet
rm dist/*.egg
python setup.py bdist_egg
cp dist/pyglet*.egg $here/lithosphere
cd $here

cd ../../setuptools-0.6c11
rm dist/*.egg
python setup.py bdist_egg
cp dist/setuptools*.egg $here/lithosphere
cd $here

cd ..
rm dist/*.egg
python setup.py bdist_egg
cp dist/lithosphere*.egg $here/lithosphere
cd $here

cp run_standalone.py lithosphere/run.py

tar czvf lithosphere.tgz lithosphere
zip lithosphere.zip -R lithosphere/*
rm -rf lithosphere
rm *.egg
