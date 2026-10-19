# nwmakefiles-python
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-01-02 | numbworks | Created. |
| 2026-07-27 | numbworks | Last update. |

## Introduction

`nwmakefiles` is a collection of reusable files and processes that streamline pre-release checks and utility actions.

**Disclaimer**: please be aware that not all the targets documented above may be available for all the projects.

## Project Structure And File Roles

An example of the project structure:

```
...
.vscode/
    ├── ...
    └── tasks.json
...
scripts/
├── nwmakefiles/
    ├── makefile
    ├── makefile-nwtimetracking
    └── makefile-nwtimetrackingcli
└── ...
src/
├── ...
├── nwtimetracking.py
├── nwtimetrackingcli.py
├── setup.py
└── setupinfo.py
...
.gitattributes
...
```

|File|Role|
|---|---|
|`tasks.json`|Contains all the tasks available via VSCode's `Run Task`. Tasks simplify the access to the `makefile*` targets.|
|`makefile`|Contains all the available targets.|
|`makefile-nwtimetracking`|Contains all the available targets for the library.|
|`makefile-nwtimetrackingcli`|Contains all the available targets for the CLI application.|
|`.gitattributes`|This enforces LF end‑of‑line formatting for Linux‑sensitive files (the `makefile*` files).|

## The Tasks File

An example of `tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "nwtimetracking: all-concise",
            "type": "shell",
            "command": "cd ${workspaceFolder}/scripts/nwmakefiles && make -f makefile-nwtimetracking all-concise",
            "problemMatcher": []
        },
        {
            "label": "nwtimetrackingcli: all-concise",
            "type": "shell",
            "command": "cd ${workspaceFolder}/scripts/nwmakefiles && make -f makefile-nwtimetrackingcli all-concise",
            "problemMatcher": []
        },
        {
            "label": "nwtimetracking: coverage-verbose",
            "type": "shell",
            "command": "cd ${workspaceFolder}/scripts/nwmakefiles && make -f makefile-nwtimetracking coverage-verbose",
            "problemMatcher": []
        },
        {
            "label": "nwtimetrackingcli: coverage-verbose",
            "type": "shell",
            "command": "cd ${workspaceFolder}/scripts/nwmakefiles && make -f makefile-nwtimetrackingcli coverage-verbose",
            "problemMatcher": []
        },
        {
            "label": "nwtimetracking: update-codecoverage",
            "type": "shell",
            "command": "cd ${workspaceFolder}/scripts/nwmakefiles && make -f makefile-nwtimetracking update-codecoverage",
            "problemMatcher": []
        },
        {
            "label": "nwtimetrackingcli: update-codecoverage",
            "type": "shell",
            "command": "cd ${workspaceFolder}/scripts/nwmakefiles && make -f makefile-nwtimetrackingcli update-codecoverage",
            "problemMatcher": []
        }
    ]
}
```

To implement it:

1. Open the folder in Visual Studio Code.
2. Update the example above according to your application and save it as `.vscode/tasks.json`.
3. Click on `Terminal` > `Run Task`  and select the task you want to run.
4. Done!

## Notes: The GitAttributes File

The `.gitattributes` file must include the following line:

```
...
# Force LF for EOL‑sensitive files (CRLF breaks them on Linux)
makefile* text eol=lf
```

If these rules were added after the corresponding files were already created, open the devcontainer terminal and apply the normalization:

```bash
git add --renormalize .
git commit -m "Apply EOL rules"
```

To verify that the rules are now applied correctly:

```bash
git ls-files --eol
```

## Notes: The Makefiles And The Pre-Release Checks

The following `makefile` targets serve as pre-release checks:

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

## Notes: The Makefiles And The Utility Actions

The following `makefile` targets serve as utility actions:

| Target Name | Description |
|---|---|
| `calculate-commitavg` | Shows the daily average time between commits, grouped by year and month. |
| `check-pythonversion` | Checks if the installed Python version is the expected one and logs a message. |
| `check-requirements` | Checks if the required dependencies match with the most recent releases on PyPi. |
| `create-classdiagram` | Generates a Mermaid class diagram for a given module file, showing only the relationships among classes. |
| `update-codecoverage`| Updates the `codecoverage-<modulename>.*` files according to the total unit test coverage. |


## Notes: The Makefiles And The Terminal

To run the `makefile` targets via Terminal:

1. Open the folder in Visual Studio Code.
2. Click on `Terminal` > `New Terminal`.
3. Run the following commands:

    ```sh
    cd /workspaces/<project_name>/scripts/nwmakefiles
    make -f makefile-<library_name> <target_name>
    ```

    ```sh
    cd /workspaces/<project_name>/scripts/nwmakefiles
    make -f makefile-<cli_name> <target_name>
    ```

4. Done!

## Notes: The Makefiles And Their Counterintuitive Syntactic Features

Considering the old-fashioned syntax adopted by both `make` and `Bash`, here a summary of its counterintuitive aspects:

| Aspect | Description |
|---|---|
| `.PHONY` | All the targets that need to be called from another target need to be listed here. |
| `SHELL := /bin/bash` | By default, `make` uses `sh`, which doesn't support some functions such as string comparison. |
| `@` | By default, `make` logs all the commands included in the target. The `@` disables this behaviour. |
| `$$` | Necessary to escape `$`. |
| `$@` | Variable that stores the target name. |
| `if [[ ... ]]` | Double square brackets to enable pattern matching. |

## Notes: `check-requirements`

By default, the `check-requirements` checks for the updatability of the dependencies defined in the devcontainer named `main`. 

If you want to target a different devcontainer in the same project:

1. Open the folder in Visual Studio Code.
2. Click on `Terminal` > `New Terminal`.
3. Run the following commands to perform the dependency check (it requires an internet connection):

    ```
    cd src
    python3
    from nwpackageversions import RequirementChecker
    RequirementChecker().check("/workspaces/<project_name>/.devcontainer/<devcontainer_name>/Dockerfile")
    ```

4. You will get a log containing a list of up-to-date and out-of-date dependencies, that you can use to decide which update to perform.
5. Done!

## Notes: `all-concise`

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

## Source

The following project is used for the examples in this document:

- [nwtimetracking](https://github.com/numbworks/nwtimetracking)

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)