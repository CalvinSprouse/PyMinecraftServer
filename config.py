"""
Workflow:
1. Establish a master directory

master_dir
- server_dir
    - server_name
        - (SERVER STUFF AS NORMAL)
    - server_name_2
        - (SERVER STUFF AS NORMAL)
- server_jar_dir (will be searched before downloading from the internet)
    - forge
        - FORGE JARS
    - regular
        - REGULAR JARS
- mods_dir (a user curated selection of mods)
- other config files (batch and shit)

2. "select operation" this is informal there is no operation command like .op = edit but is just used to describe work

3-load/edit.
    a. Select server from server_dir (pass in a str name return server not found error)
        args = name: str
        return a server loader object?
    b. now in the server loader/editor
        functions to edit properties of the server.properties file, will be opened and saved on EVERY operation to
        simplify
        specific function to change world/reset world (by deleting world file and changing server.properties)
        functions to view current properties
        change ram allocation by modifying start.bat (in every server)
        function for mod installation
            checks if the server.jar is a forge jar
            if the passed location of the mod.jar is just a name, check local dir
            else check the exact location and copy the mod to the mods folder
    c. run server
        spawn a seperate process and run the server, launch commands available through args like -nogui and shit
        create some intercommunication method but prevent editing the active server/overwriting it

3-create.
    a. name, version, overwrite=False
        if name exist and not overwrite raise exists exception
        if version not in jar_dir check online if that doesnt exist raise version exception
        if all is good create a folder in the server_dir with the name, copy the proper jars and start batch script
            run it, accept eula, run it again
        if all is still good return a server loader object (unless this is all in one class which it should be)
        else raise an exception and delete the new folder

4. repeat

Design Strategy:
no saving information relevant to a single server in the class, instead everything should be loaded in from the
    files existing on the computer, the only thing saveable is the reference to a running server
do not implement design features that belong with something like a discord server or other applications, needlessly
    complex and they can handle it themselves, instead include lots of getter methods
do however implement lots of safety, not allowing running servers to be edited/deleted, "deleting" a server that has
    worked (hasnt thrown an error in creation) should instead just move them to a deleted folder or something of the
    sort
start the servers with the start.bat file that way program and end-user interact similarly
allow the user create a start.bat.template file which can be edited for each server
for jars create a naming scheme function/lambda (for all things named specifically actually)
"""