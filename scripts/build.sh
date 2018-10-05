cd purly

# clean up possible old install
if [ -d "py/purly/static" ]; then
  rm -rf py/purly/static
fi
mkdir py/purly/static

# build js packages
cd js
npm install
npm run bootstrap
npm run build
cd ../

# copy built files to py
cp -r js/packages/purly-widget/build py/purly/static/widget
cp -r js/packages/purly-board/build py/purly/static/board

cd ../
