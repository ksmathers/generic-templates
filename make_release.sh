#!/bin/bash
#set -x
version=$1
if [ -z $version ] ; then
    echo "make_release.sh <version>"
fi
#sed -i "s/version = \"[^\"]\"/version = \"$version\"/" setting.sh
sed -e "s/version = .*/version = \"$version\",/" -i.bak setup.py
git add setup.py
git commit -m "Release $version"
git tag release-$version
git push
git push --tags
