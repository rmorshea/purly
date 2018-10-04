cd purly

# clean up possible old install
if [ -d "py/purly/static" ]; then
  rm -rf py/purly/static
  mkdir py/purly/static
fi

# build js packages
cd js
npm install
lerna bootstrap
lerna run build
cd ../

# copy built files to py
cp -r js/packages/purly-widget/build py/purly/static/widget
cp -r js/packages/purly-board/build py/purly/static/board

cd ../
