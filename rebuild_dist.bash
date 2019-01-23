#!/bin/bash

NAME=MH_Community
ZNAME="${NAME}_for_blender"
BLVER=280
ZIP="${ZNAME}_${BLVER}.zip"
DIR=`pwd`

rm blender_distribution/$ZIP
cd blender_source
zip -r ../blender_distribution/$ZIP $NAME --exclude $NAME/\*__pycache__\* --exclude \*.pyc

cp ../blender_distribution/$ZIP /tmp
cd /tmp
rm -rf MH_Community
unzip $ZIP
sed -i -e 's/"blender": (2, 80/"hejhopp": (2, 79/g' MH_Community/__init__.py
BLVER=279
ZIP="${ZNAME}_${BLVER}.zip"
zip -r $ZIP $NAME

cd $DIR
cp /tmp/$ZIP blender_distribution

