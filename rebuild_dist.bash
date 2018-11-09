#!/bin/bash

NAME=MH_Community
ZIP=$NAME.zip
DIR=`pwd`

rm blender_distribution/$ZIP
cd blender_source
zip -r ../blender_distribution/$ZIP $NAME --exclude $NAME/\*__pycache__\* --exclude \*.pyc
cd $DIR

