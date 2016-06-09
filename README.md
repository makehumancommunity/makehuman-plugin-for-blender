# Community plugins

Contributed plugins for makehuman and related programs

## Existing plugins

So far this repo contains the following plugins:

### 1_mhapi

MakeHuman plugin. This doesn't do anything in itself, it just provides convenience methods
for getting info about stuff in makehuman or controlling stuff in makehuman. See README
in the directory.

### 8_server_socket

MakeHuman plugin, opens a socket server inside MH and accepts some basic commands.

### mh_sync_mesh

Blender plugin. Requires MH to have 8_server_socket. Synchronizes vertex coordinates against
the current state in MakeHuman.

