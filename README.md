# Community plugins

Contributed plugins for makehuman and related programs

## Existing plugins

So far this repo contains the following plugins:

### makehuman/1_mhapi

MakeHuman plugin. This doesn't do anything in itself, it just provides convenience methods
for getting info about stuff in makehuman or controlling stuff in makehuman. See README
in the directory.

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

