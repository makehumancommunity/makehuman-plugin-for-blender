# CLI

These are scripts that are intended to run from command line

## MH Remote Control (mhrc)

This is a set of commands for getting and setting stuff in makehuman. It 
requires that 8_socket_server is installed, enabled and running in 
MakeHuman.

### genericCommand.py

Send a generic command to the socket server (8_socket_server plugin) and print 
the resulting contents of the data key of the response object. 

For example

    python genericCommand getCoord
    
would print the vertex coordinates of the current mesh.



