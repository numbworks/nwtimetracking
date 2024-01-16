# nwtimetrackingmanager
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2023-08-21 | numbworks | Created. |
| 2024-01-16 | numbworks | Updated to v1.3.0. |

## Introduction

`nwtimetrackingmanager` is a `Jupyter Notebook` designed to analyze the Excel file I use to annotate the durations of all my sessions of extra work and continuos learning, so that I can run analyses on them. 

This software is born to overcome the lack of support for durations (timedeltas) in Excel.

This project may not be useful for many (not generic enough), but I decided to upload it to `Github` anyway, in order to showcase my way of working when I face similar data analysis tasks and I decide to tackle them with `Python` and `Jupyter Notebook`.

## Getting Started

In order to run this Jupyter Notebook:

1. Download and install [Python 3.x](https://www.python.org/downloads/);
      - This has been tested with the following Python version: `3.11.0`
2. Download and install [Visual Studio Code](https://code.visualstudio.com/Download);
3. Download and install the following extension within Visual Studio Code: [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
4. Open a terminal and run the following commands:
    - ```python.exe -m pip install --upgrade pip```
5. Launch Visual Studio Code and open `src/nwtimetrackingmanager.ipynb`;
6. Edit the `SettingCollection` object according to your needs;
7. Click on `Run All`;
8. Done!

If, for some reason the `Setup` block doesn't work, you can open a terminal and run the following commands to install the required packages:

- ```pip3 install pandas==1.5.2```
- ```pip3 install numpy==1.24.0```
- ```pip3 install openpyxl==3.0.10```
- ```pip3 install coverage==7.2.3```
- ```pip3 install parameterized==0.9.0```

To run the unit tests, open a terminal and run the following commands:

- `cd <base_folder>\nwtimetrackingmanager\tests`
- `clear && coverage run -m unittest nwtimetrackingmanagertests.py && coverage report`

## For Developers

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