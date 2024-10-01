# nwtimetracking
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2023-08-21 | numbworks | Created. |
| 2024-01-16 | numbworks | Updated to v1.3.0. |
| 2024-01-21 | numbworks | Updated to v2.0.0. |
| 2024-03-19 | numbworks | Updated to v3.0.0. |
| 2024-05-19 | numbworks | Updated to v3.2.0. |
| 2024-05-20 | numbworks | Updated to v3.3.0. |
| 2024-08-12 | numbworks | Updated to v3.4.0. |
| 2024-10-01 | numbworks | Updated to v3.7.0. |

## Introduction

`nwtimetracking` is a `Jupyter Notebook` designed to analyze the Excel file I use to annotate the durations of all my sessions of extra work and continuos learning, so that I can run analyses on them. 

This software is born to overcome the lack of support for durations (timedeltas) in Excel.

This project may not be useful for many (not generic enough), but I decided to upload it to `Github` anyway, in order to showcase my way of working when I face similar data analysis tasks and I decide to tackle them with `Python` and `Jupyter Notebook`.

## Getting Started

To run this application on Windows and Linux:

1. Download and install [Visual Studio Code](https://code.visualstudio.com/Download);
2. Download and install [Docker](https://www.docker.com/products/docker-desktop/);
3. Download and install [Git](https://git-scm.com/downloads);
4. Open your terminal application of choice and type the following commands:

    ```
    mkdir nwtimetracking
    cd nwtimetracking
    git clone https://github.com/numbworks/nwtimetracking.git
    ```

5. Launch Visual Studio Code and install the following extensions:

    - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
    - [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
    - [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
    - [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
    - [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)

6. In order for the Jupyter Notebook to automatically detect changes in the underlying library, click on <ins>File</ins> > <ins>Preferences</ins> > <ins>Settings</ins> and change the following setting as below:

    ```
    "jupyter.runStartupCommands": [
        "%load_ext autoreload", "%autoreload 2"
    ]
    ```

7. In order for Pylance to perform type checking, set the `python.analysis.typeCheckingMode` setting to `basic`;
8. Click on <ins>File</ins> > <ins>Open folder</ins> > `nwtimetracking`;
9. Click on <ins>View</ins> > <ins>Command Palette</ins> and type:

    ```
    > Dev Container: Reopen in Container
    ```

10. Wait some minutes for the container defined in the <ins>.devcointainer</ins> folder to be built;
11. Open the notebook file (<ins>src/nwtimetracking.ipynb</ins>);
12. Edit the `SettingBag` object according to your needs;
13. Click on <ins>Run All</ins>;
14. Done!

## Unit Tests

To run the unit tests in Visual Studio Code (while still connected to the Dev Container):

1.  click on the <ins>Testing</ins> icon on the sidebar, right-click on <ins>tests</ins> > <ins>Run Test</ins>;
2. select the Python interpreter inside the Dev Container (if asked);
3. Done! 

To calculate the total unit test coverage in Visual Studio Code (while still connected to the Dev Container):

1. <ins>Terminal</ins> > <ins>New Terminal</ins>;
2. Run the following commands to get the total unit test coverage:

    ```
    cd tests
    coverage run -m unittest nwtimetrackingtests.py
    coverage report --omit=nwtimetrackingtests.py
    ```

3. Run the following commands to get the unit test coverage per class:

    ```
    cd tests
    coverage run -m unittest nwtimetrackingtests.py
    coverage html --omit=nwtimetrackingtests.py && sed -n '/<table class="index" data-sortable>/,/<\/table>/p' htmlcov/class_index.html | pandoc --from html --to plain && sleep 3 && rm -rf htmlcov
    ```

4. Done!

## Known Issues - nwshared

If `nwshared` creates some issues for you, please refer to [its documentation on Github](https://github.com/numbworks/nwshared/blob/master/docs/docs-nwshared.md).

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)