## Run all tests via discover
* cd to the project root directory
* run `python -m unittest discover`

## Run a single test
* cd to the project root directory
* run `python -m unittest test.<filename without .py>`
* e.g. `python -m unittest test.test_nacl_git`

## nosetests
* pip install nose
* cd to the project test directory
* run `nosetests <filename with .py` for a single test or
* `nosetests --exe` for running all tests.

## Code coverage
* run `pip install coverage`
* followed by `nosetests --exe --with-coverage`

Oh my God! Better try this:
`nosetests test_nacl_gitlabapi.py --with-coverage --cover-package=nacl.gitlabapi`

This is usefull to gather informations about LoC that are not covered by any unittests.
