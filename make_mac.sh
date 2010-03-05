echo cleanup before build
rm -rf dist/lithosphere.dmg dist/lithosphere dist/lithosphere.app build

#basic setup
python setup.py py2app #--iconfile data/ship.icns

echo touching up the distribution
export py_dir=dist/lithosphere.app/Contents/Resources/lib/python2.5
export site_packages=$py_dir/site-packages
unzip -d $site_packages $py_dir/site-packages.zip
rm $py_dir/site-packages.zip

echo creating a disc image
mkdir dist/lithosphere
mv dist/lithosphere.app dist/lithosphere
ln -s /Applications dist/lithosphere
hdiutil create dist/lithosphere.dmg -srcfolder dist/lithosphere
rm -rf dist/lithosphere
