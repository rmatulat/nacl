"""
The nacl package

Classes, functions and methods of the nacl package
are mainly written to support the development of the nacl-* scripts
for managing salt infrastructures.
My no means they are intended to be used in another context.

Following modules are included:
    - base: Basic functions needed in different places
    - decorator: Especially logging is done with decorators
    - exceptions: Put custom exceptions here
    - fileutils: If it comes to FS operations like reading a file
    - flow: Contains everything for nacl-flow
    - git: Contains everything for nacl-git
    - gitapi: This SHOULD contain an abstraction layer for operations against
              gitlab or github servers. But it is a bloody mess yet and has
              nothing to do with what it was supposed to.
    - gitlabapi: Communication with an gitlab instance
    - helper: Some helper for colorizing output etc.

Let's start refactoring.
"""
