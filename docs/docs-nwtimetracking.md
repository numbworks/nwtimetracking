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

## Introduction

`nwtimetracking` is a `Jupyter Notebook` designed to analyze the Excel file I use to annotate the durations of all my sessions of extra work and continuos learning, so that I can run analyses on them. 

This software is born to overcome the lack of support for durations (timedeltas) in Excel.

This project may not be useful for many (not generic enough), but I decided to upload it to `Github` anyway, in order to showcase my way of working when I face similar data analysis tasks and I decide to tackle them with `Python` and `Jupyter Notebook`.

## Getting Started

In order to run this Jupyter Notebook:

1. Download and install [Python 3.x](https://www.python.org/downloads/);
      - This has been tested with the following Python version: `3.12.1`
2. Download and install [Visual Studio Code](https://code.visualstudio.com/Download);
3. Download and install the following extension within Visual Studio Code: [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
4. Open a terminal and run the following commands:
    - ```python.exe -m pip install --upgrade pip```
5. Launch Visual Studio Code and open `src/nwtimetracking.ipynb`;
6. Edit the `SettingBag` object according to your needs;
7. Click on `Run All`;
8. Done!

If, for some reason the `Setup` block doesn't work, you can open a terminal and run the ```pip install``` commands to install the required packages:

If `nwshared` creates some issues for you, please refer to [its documentation on Github](https://github.com/numbworks/nwshared/blob/master/docs/docs-nwshared.md).

## For Developers

To run the unit tests, open a terminal and run the following commands:

- `cd <base_folder>\nwtimetracking\tests`
- `coverage run -m unittest nwtimetrackingtests.py`
- `coverage report`

To enable the unit test runner in `Visual Studio Code`:

1. create a `.vscode` folder in `cd <base_folder>\nwtimetracking\`;
2. add a `settings.json` file and paste the following content in it:

  ```json
  {
      "python.testing.unittestArgs": [
          "-v",
          "-s",
          "./tests",
          "-p",
          "*tests.py"
      ],
      "python.testing.pytestEnabled": false,
      "python.testing.unittestEnabled": true
  }  
  ```
3. save the file and close `Visual Studio Code`;
4. open `Visual Studio Code` -> `File` -> `Open Folder` and select `cd <base_folder>\nwtimetracking\`;
5. if the testing icon doesn't appear on the sidebar, just open whatever `*.py` file;
6. Done!

To run type checking:

- `cd <base_folder>\nwtimetracking\`
- `mypy src --disable-error-code import-untyped --disable-error-code func-returns-value --disable-error-code import-untyped --disable-error-code annotation-unchecked`
- `mypy tests --disable-error-code import-untyped --disable-error-code func-returns-value --disable-error-code import-untyped --disable-error-code annotation-unchecked`

In order to perform development work on this project in a comfortable way, you might want to enable the auto-reload / auto-refresh of the content of `Python` modules used in `Jupyter Notebook`:

1.	`Visual Studio Code` > `File` > `Preferences` > `Settings`;
2.	Search for the following setting and change it as below:

  ```json
    "jupyter.runStartupCommands": [
        "%load_ext autoreload", "%autoreload 2"
    ]
  ```

3.	Done!

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)