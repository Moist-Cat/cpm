The Card Package Manager 
===========================

## What problem does this software solve?
Gives a centralized tool to manage packages (file + image + metadata) and makes them easy to find
  
## Requirements
To install all requirements, use the following snippet after installing python on your machine.

    pip install -r requirements.txt

Or just:

    pip install cpm

## Portability

Depending on what platform you are on, the executable is different.

    cpm

Is intended for GNU/Linux distributions

    cpm.bin

Should work on Windows. But I don't have a Windows machine/VN to test the package, so expect trouble.

## Quick guide

    cpm -h

Shows the help
    cpm search

Lists the packages hosted on the remote repository

    cpm info [name]

Shows information about the package [name]


    cpm download [name]

Downloads the package [name] and all its dependencies.

    cpm compile [name]

Downloads the package [name], and all its dependencies; and compiles the files (.lorebook) into a single file that can be imported.

## ...Problems?
### Be sure you are using the correct executable for your OS.

    cpm.bin

For Windows

   cpm

For GNU/Linux.

### Logs
There is a helpful command

    cpm debug

That will print the logs on the terminal screen. Be sure to include either the output or the client.audit file with you when reporting a bug.

### Use quotes when using spaces on the terminal

    cpm info "Hakurei Reimu"

    cpm download "Hakurei Reimu, Kirisame Marisa"

Although using spaces or long names when naming packages is not recommended.

### Avoid commas in the package name and tags
Since blank characters are supported, multiple items need to be comma separated. So don't use them anywhere else. (especially on the name or the tags)

### Third-party files
 Use the full URL for files, including the scheme "https". Also, make sure the URL doesn't point to an insecure website served with HTTPS.
