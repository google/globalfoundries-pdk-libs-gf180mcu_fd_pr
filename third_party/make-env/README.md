# Makefile for create (conda) environments

![Build Status](https://travis-ci.org/SymbiFlow/make-env.svg?branch=master)
![License](https://img.shields.io/github/license/SymbiFlow/make-env.svg)

This repository contains a Makefile to make it easy to set up a conda
environment and then run commands inside the environment.

# Using

## Step 1 - Add make-env to your repository

### Option 1a -- git submodules

The [`make-env`](https://github.com/SymbiFlow/make-env) git
repository can be added as a
[`git submodule`](https://git-scm.com/book/en/v2/Git-Tools-Submodules) of your
own git repository.

#### Adding using `git submodule`

```bash
git submodule add https://github.com/SymbiFlow/make-env.git third_party/make-env
```

#### Updating using `git submodule`

It is recommended you use an "auto rolling" dependency bot which sends you a
pull request every time the upstream module moves forward.

```bash
# TODO: Add stuff here.
```


### Option 1b -- `git subtrees`

The [`make-env`](https://github.com/SymbiFlow/make-env) git
repository can be directly imported into your repository using
[`git subtree`](https://www.atlassian.com/git/tutorials/git-subtree).

`git subtree`s offer a number of advantages over `git submodule`s, they
include;

 * The contents of the subtree are directly included in your own tree, meaning
   no extra clone nor recursive clone is needed. If the upstream source
   disappears, you still have a complete copy of the repository contents.

 * Edits can be done and sent upstream easily.


#### Adding using `git subtree`

```bash
git remote add -f make-env https://github.com/SymbiFlow/make-env.git
git subtree add --prefix third_party/make-env make-env master
git fetch make-env master
```

#### Updating using `git subtree`

```bash
git subtree pull --prefix third_party/make-env make-env master
```

## Step 2 - Create a Makefile

Create a Makefile which sets;
 * `TOP_DIR` -- the directory where an `env` directory will be created in.
 * `REQUIREMENTS_FILE` -- [A pip `requirements.txt` file](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format).
 * `ENVIRONMENT_FILE` -- [A conda `environment.yml` file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

Include the `third_party/make-env/conda.mk` file.

Make your targets depend on `$(CONDA_ENV_PYTHON)` -- probably as an "order only
dependency".

Use `$(IN_CONDA_ENV)` before the commands you wish to run inside the conda
environment.

A [template Makefile](Makefile.template) is provided, see below;

```Makefile

# The top directory where environment will be created.
TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

# A pip `requirements.txt` file.
# https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format
REQUIREMENTS_FILE := requirements.txt

# A conda `environment.yml` file.
# https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
ENVIRONMENT_FILE := environment.yml

include third_party/make-env/conda.mk

# Example make target which runs commands inside the conda environment.
test-command: | $(CONDA_ENV_PYTHON)
	@$(IN_CONDA_ENV) echo "Python is $$(which python)"
	@$(IN_CONDA_ENV) python --version
```

# Testing

To make sure that `make-env` continues to work correctly and the template
Makefile is up to date, an example environment can be found in the test
directory.


```shell
# core.symlinks=true is needed so windows creates the symlinks.
git clone -c core.symlinks=true https://github.com/SymbiFlow/make-env.git
cd make-env/test
make test-command
```

# Todo list

 - [ ] Make sure the conda can be disabled and system tooling be used directly.
 - [ ] Add support for other types of environments;
   - [ ] Docker provided dependencies.
   - [ ] System python + virtualenv.
   - [ ] (maybe?) nix-os provided dependencies

# Contributing

There are a couple of guidelines when contributing to this project which are
listed here.

### Sending

All contributions should be sent as
[GitHub Pull requests](https://help.github.com/articles/creating-a-pull-request-from-a-fork/).

### License

All software (code, associated documentation, support files, etc) in the
Project X-Ray repository are licensed under the very permissive
[ISC Licence](https://opensource.org/licenses/ISC). A copy can be found in the
[`LICENSE`](LICENSE) file.

All new contributions must also be released under this license.

### Code of Conduct

By contributing you agree to the [code of conduct](CODE_OF_CONDUCT.md). We
follow the open source best practice of using the [Contributor
Covenant](https://www.contributor-covenant.org/) for our Code of Conduct.

### Sign your work

To improve tracking of who did what, we follow the Linux Kernel's
["sign your work" system](https://github.com/wking/signed-off-by).
This is also called a
["DCO" or "Developer's Certificate of Origin"](https://developercertificate.org/).

**All** commits are required to include this sign off and we use the
[Probot DCO App](https://github.com/probot/dco) to check pull requests for
this.

The sign-off is a simple line at the end of the explanation for the
patch, which certifies that you wrote it or otherwise have the right to
pass it on as a open-source patch.  The rules are pretty simple: if you
can certify the below:

        Developer's Certificate of Origin 1.1

        By making a contribution to this project, I certify that:

        (a) The contribution was created in whole or in part by me and I
            have the right to submit it under the open source license
            indicated in the file; or

        (b) The contribution is based upon previous work that, to the best
            of my knowledge, is covered under an appropriate open source
            license and I have the right under that license to submit that
            work with modifications, whether created in whole or in part
            by me, under the same open source license (unless I am
            permitted to submit under a different license), as indicated
            in the file; or

        (c) The contribution was provided directly to me by some other
            person who certified (a), (b) or (c) and I have not modified
            it.

	(d) I understand and agree that this project and the contribution
	    are public and that a record of the contribution (including all
	    personal information I submit with it, including my sign-off) is
	    maintained indefinitely and may be redistributed consistent with
	    this project or the open source license(s) involved.

then you just add a line saying

	Signed-off-by: Random J Developer <random@developer.example.org>

using your real name (sorry, no pseudonyms or anonymous contributions.)

You can add the signoff as part of your commit statement. For example:

    git commit --signoff -a -m "Fixed some errors."

*Hint:* If you've forgotten to add a signoff to one or more commits, you can use the
following command to add signoffs to all commits between you and the upstream
master:

    git rebase --signoff upstream/master
