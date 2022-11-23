# integration tests
## Requirements
The integration tests rely directly on docker-compose and assume
that functionals `docker-compose`[^1] and `docker`[^2] commands are available in the environment.

Required python dependencies are made available in the [test-requirements.txt](./test-requirements.txt) file.

## Docker image
The tests rely on a containerized deployment of the codebase.
The container image can be built using the [Dockerfile](./docker/confgend.Dockerfile)
available in the [docker](./docker) subdirectory.
To build the image, this command can be run(assuming the current directory as the working directory):
```
docker build -f docker/confgend.Dockerfile -t wazoplatform/wazo-confgend-test:local ..
```
To test that the image is functional:
```
docker run --rm -it -v $(readlink ..):/usr/local/src/wazo-confgend wazoplatform/wazo-confgend-test:local
```
(note that the project root is mounted as a volume to provide in-development source code for testing).

Once the image is made available locally, the docker-compose configurations should be able to use it and pull any other required images from the relevant registries.

## Running tests

The tests suite uses `pytest`[^3], provided through the [requirements file](./tests-requirements.txt).
To run a single test file and all tests contained:
```
pytest suite/test_confgen.py
```
To run all tests:
```
pytest suite/
```
and to run only tests matching a specific marker and a specified name pattern:
```
pytest -m 'critical' -k 'pjsip_conf' suite/
```

## shell.sh
The [shell.sh](./shell.sh) is a helper script that opens a new shell with the proper environment for running test commands.
It ensures
* a virtual environment is created(if missing) and activated with the required python dependencies installed
* the right docker-compose environment(see [./assets](./assets) subdirectory) is deployed,
  through the help of the [`denv`](https://github.com/wazo-platform/denv) utility

resulting in an environment ready for testing(by then manually running the test cases in (./suite)[./suite]).
When the shell is exited, the docker-compose environment is gracefully shutdown.
The shell can be customized through these environment variables:
* `VENV_PATH`: path to the python virtual environment(will only be created if a directory does not already exists)
* `PYTHON`: the python executable to use to create the virtual environment
* `DENV`: The path to the `denv` script to be sourced into the new shell.
  By default it is assumed to be available at `$WAZO_ROOT/denv/denv`.
* `WAZO_ROOT`: path to the parent directory of all wazo projects, including `denv`. Defaults to `$HOME/wazo`.

By default, the [shell.sh](./shell.sh) script will run a new interactive shell using the `$SHELL`.
An argument can also be provided to the script to run a custom command:
```
bash script.sh pytest suite/
```
which results in
1. `pytest` and other test python requirements are installed and made available in a virtual environment
2. `denv` is made available and `denv enter` is invoked, deploying the test docker-compose environment
3. `pytest suite/` is invoked, running the test suite against the deployed docker-compose stack
4. after completion of the command, the shell exits, gracefully bringing down and removing the docker-compose resources,
and discarding any effects on the shell environment(except that the virtual environment created still remains for subsequent invocation).

## TODO
1. obtain reference dataset for tests:
    a. generate dump of relevant database tables from reference environment
        (look in asterisk conf dao for list of relevant tables, provide dump script)
    b. generate reference confgen outputs for all configs from reference environment
        (provide script to run wazo-confgen for each config in reference environment)
2. ensure test datasets are available to test containers
    a. place postgresql dump script in entrypoint volume
    b. place reference output in assets/data volume


[^1]: https://docs.docker.com/compose/
[^2]: https://docs.docker.com/
[^3]: https://docs.pytest.org/en/7.2.x/
