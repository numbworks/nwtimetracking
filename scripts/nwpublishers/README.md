# nwtimetracking

## Introduction

This packages consists of the following modules:

- `nwtimetracking` is a library that can run several automated data analysis tasks on a time tracking file and save the results as a PDF report. It’s designed to facilitate and gamify a continuous learning journey.
- `nwtimetrackingcli` is a command-line application built on the top of `nwtimetracking`.

## Pre-Requisites

In order to work, this library requires to be run against a local Git repository and that Git itself is installed on the machine.

## Getting Started

I'll use Debian as operating system, but the concept is similar for Windows or Mac.

Procedure:

1. Install `pip` and `venv`:

```sh
sudo apt install python3-pip python3.12-venv
```

2. Create a virtual environment:

```sh
python3 -m venv /tmp/nwtimetracking
source /tmp/nwtimetracking/bin/activate
```

3. Download and install the package:

```sh
pip install nwtimetracking
```

4. Enter in the interactive Python environment:

```sh
python3
```
```
Python 3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

5. Try out if the library works:

```python
from nwtimetracking import TTReportManager

report_manager : TTReportManager = TTReportManager()
```

6. Exit from the interactive Python environment:

```python
exit()
```

7. Try out if the CLI application works:

```sh
nwtimetrackingcli
```

8. Deactivate and delete the virtual environment:

```sh
deactivate
rm -rf /tmp/nwtimetracking
```

9. Done!

## Examples

Run it against a reading list:

```sh
root@e584fefc57f0:/# alias nwtime="python src/nwtimetrackingcli.py"
root@e584fefc57f0:/# nwtime --input_path "/data/Time Tracking.xlsx" --nrow 2040
```

```
***********************************************************
'##::: ##:'##:::::'##:'########:'####:'##::::'##:'########:
 ###:: ##: ##:'##: ##:... ##..::. ##:: ###::'###: ##.....::
 ####: ##: ##: ##: ##:::: ##::::: ##:: ####'####: ##:::::::
 ## ## ##: ##: ##: ##:::: ##::::: ##:: ## ### ##: ######:::
 ##. ####: ##: ##: ##:::: ##::::: ##:: ##. #: ##: ##...::::
 ##:. ###: ##: ##: ##:::: ##::::: ##:: ##:.:: ##: ##:::::::
 ##::. ##:. ###. ###::::: ##::::'####: ##:::: ##: ########:
..::::..:::...::...::::::..:::::....::..:::::..::........::
****************************************Version: 6.1.0*****

command: 'save'
input_path: '/data/Time Tracking.xlsx'
nrows: '2082'
folder_path: 'None'

The PDF report has been successfully saved.
```

Run it against a reading list with custom `folder_path`:

```sh
root@e584fefc57f0:/# alias nwtime="python src/nwtimetrackingcli.py"
root@e584fefc57f0:/# nwtime --input_path "/data/Time Tracking.xlsx" --nrow 2040 --folder_path "/home/nwtimetracking/"
```

## Links

- Source: https://github.com/numbworks/nwtimetracking
- License: https://github.com/numbworks/nwtimetracking/blob/master/LICENSE

## Total Downloads (PyPi)

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/nwtimetracking?period=total&units=NONE&left_color=BLACK&right_color=BLUE&left_text=TOTAL+DOWNLOADS)](https://pepy.tech/projects/nwtimetracking)