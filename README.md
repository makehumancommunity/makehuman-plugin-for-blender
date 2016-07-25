# Community plugins

Contributed plugins for makehuman and related programs

## How to install

For the makehuman plugins:

* Download the entire repository as a zip file (you should see a green button "clone or download" on github)
* Figure out where your makehuman plugins directory is. On windows, it's usually a dir called "plugins" where you unzipped MH. On linux it is in /usr/share/makehuman/plugins if you installed from PPA
* Copy everything from the makehuman directory in the zip you downloaded to the plugins directory
* All plugins should autoenable the next time you start MH

For the blender plugin(s) : 

* Download the file blender_distribution/MH_Community.zip (or find it locally if you downloaded the zip above)
* DO NOT UNZIP THIS FILE
* In blender go to file -> user preferences -> addons
* Click "install from file"
* Navigate to the MH_Community.zip file

## Existing plugins

So far this repo contains the following plugins:

### makehuman/1_mhapi

MakeHuman plugin. This doesn't do anything in itself, it just provides convenience methods
for getting info about stuff in makehuman or controlling stuff in makehuman. See README
in the directory.

### makehuman/8_community_assets

MakeHuman plugin for downloading assets from the community repos. This depends on 1_mhapi

### makehuman/8_server_socket

MakeHuman plugin, opens a socket server inside MH and accepts some basic commands. This
depends on 1_mhapi

### blender/mh_sync

Blender plugin. Requires MH to have 8_server_socket. Synchronizes various aspects of the
human versus a running instance of MH. Currently supports

* Synchronizing vertices
* Synchronizing pose

## Command line scripts

In the "cli" directory there are scripts which are intended to run from command line, 
and which either interact with the plugins or are used for the management of them

