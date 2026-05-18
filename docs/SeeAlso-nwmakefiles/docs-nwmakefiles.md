# nwmakefiles
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-01-02 | numbworks | Created. |
| 2026-03-30 | numbworks | Last update (1.0.0). |

## Introduction

`nwmakefiles` is a collection of reusable Makefiles that streamline pre-release checks and useful actions for Python applications.

## Overview

This software package ships with a group of makefiles that include two types of targets:

- Pre-Release Checks
- Useful Actions (`calculate-commitavg`, `check-pythonversion`, ...)

The group is composed by:

- One `makefile` containing all the available targets
- One `makefile-*` for every Python module (where `*` is a module identifier)

An example of the structure for an application that consists of a library and a CLI:

```
...
/scripts/
└── nwmakefiles/
    ├── makefile
    ├── makefile-<library_name>
    └── makefile-<cli_name>
...
```

## Getting Started

1. Launch Visual Studio Code;
2. Click on <ins>File</ins> > <ins>Open folder</ins> > `<project_name>`;
3. <ins>Terminal</ins> > <ins>New Terminal</ins>;
4. Run the following commands:

    ```sh
    cd /workspaces/<project_name>/scripts/nwmakefiles
    make -f makefile-<library_name> <target_name>
    ```

    ```sh
    cd /workspaces/<project_name>/scripts/nwmakefiles
    make -f makefile-<cli_name> <target_name>
    ```

5. Done!

Additionally, the most frequently used targets are available in VSCode via <ins>Terminal</ins> > <ins>Run Task</ins> > `<target_identifier>`.

## The Pre-Release Checks

The following `makefile` targets are the pre-release checks:

| Target Name | Description |
|---|---|
| `changelog-concise` | Checks if latest `CHANGELOG` entry matches matches with `makefile`'s `MODULE_VERSION`. |
| `clear` | Clears the terminal screen. |
| `codemetrics-concise` | Same as `codemetrics-verbose`, but outputs a one‑line status. |
| `codemetrics-verbose` | Runs a cyclomatic complexity analysis a given module file. |
| `compile-concise` | Same as `compile-verbose`, but outputs a one‑line status. |
| `compile-verbose` | Runs `python` command against a given module file. |
| `coverage-concise` | Same as `coverage-verbose`, but outputs a one‑line status.|
| `coverage-verbose` | Runs a unit test coverage calculation task against the library and logs the % per class. |
| `docstrings-concise` | Same as `docstrings-verbose`, but outputs a one‑line status. |
| `docstrings-verbose` | Lists all the methods that lack of docstring. |
| `makefile-info` | Outputs key-information about the invoked `makefile`. |
| `setupinfo-concise` | Checks if `MODULE_VERSION` in `setupinfo.py` matches with `makefile`'s `MODULE_VERSION`. |
| `tryinstall-concise` | Same as `tryinstall-verbose`, but outputs a one‑line status. |
| `tryinstall-verbose` | Simulates a `pip install` and logs everything. |
| `type-concise` | Same as `type-verbose`, but outputs a one‑line status. |
| `type-verbose` | Runs a type‑checking task on the given module file and logs any mismatches. |
| `unittest-concise` | Same as `unittest-verbose`, but outputs a one‑line status. |
| `unittest-verbose` | Runs `python` command against the test files. |
| `all-concise` | Runs all the pre-release verification tasks and logs a one‑line status for each of them. |

## The Useful Actions

The following `makefile` targets are the useful actions:

| Target Name | Description |
|---|---|
| `calculate-commitavg` | Shows the daily average time between commits, grouped by year and month. |
| `check-pythonversion` | Checks if the installed Python version is the expected one and logs a message. |
| `check-requirements` | Checks if the required dependencies match with the most recent releases on PyPi. |
| `create-classdiagram` | Generates a Mermaid class diagram for a given module file, showing only the relationships among classes. |
| `update-codecoverage`| Updates the codecoverage-<modulename>.* files according to the total unit test coverage. |

## Counterintuitive Syntactic Features

Considering the old-fashioned syntax adopted by both `make` and `Bash`, here a summary of its counterintuitive aspects:

| Aspect | Description |
|---|---|
| `.PHONY` | All the targets that need to be called from another target need to be listed here. |
| `SHELL := /bin/bash` | By default, `make` uses `sh`, which doesn't support some functions such as string comparison. |
| `@` | By default, `make` logs all the commands included in the target. The `@` disables this behaviour. |
| `$$` | Necessary to escape `$`. |
| `$@` | Variable that stores the target name. |
| `if [[ ... ]]` | Double square brackets to enable pattern matching. |

## Notes About `check-requirements`

By default, the `check-requirements` checks for the updatability of the dependencies defined in the devcontainer named `main`. 

If you want to target a different devcontainer in the same project:

1. Launch Visual Studio Code;
2. Click on <ins>File</ins> > <ins>Open folder</ins> > `<project_name>`;
3. <ins>Terminal</ins> > <ins>New Terminal</ins>;
4. Run the following commands to perform the dependency check (it requires an internet connection):

    ```
    cd src
    python3
    from nwpackageversions import RequirementChecker
    RequirementChecker().check("/workspaces/<project_name>/.devcontainer/<devcontainer_name>/Dockerfile")
    ```

5. You will get a log containing a list of up-to-date and out-of-date dependencies, that you can use to decide which update to perform.
6. Done!

## Notes About `all-concise`

The expected outcome for `all-concise` is:

```
MODULE_NAME: <module_name>
MODULE_VERSION: 1.0.0
COVERAGE_THRESHOLD: 70%
[OK] changelog-concise: 'CHANGELOG' updated to current version!
[OK] codemetrics-concise: the cyclomatic complexity is excellent ('A').
[OK] compile-concise: compiling the library throws no issues.
[WARNING] coverage-concise: unit test coverage < 70%.
[WARNING] docstrings-concise: not all methods have docstrings.
[OK] setupinfo-concise: 'setupinfo.py' updated to current version!
[OK] tryinstall-concise: installation process works.
[OK] type-concise: passed!
[OK] unittest-concise: '144' tests found and run.
```

## Disclaimer

Please be aware that not all the targets documented above are available for all the projects.

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)