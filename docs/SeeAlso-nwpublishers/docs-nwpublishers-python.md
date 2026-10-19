# nwpublishers-python
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-09-29 | numbworks | Created. |
| 2026-09-29 | numbworks | Last update. |

## Introduction

This guide collects all the information required to publish a `nw` package using the `nwpublisher.py` script.

## Pre-Requisites

Before integrating `nwpublishers` inside your project, please append the following block to the `.gitignore` file:

```
# nwpublishers
TESTPYPI_API_KEY.txt
PYPI_API_KEY.txt
```

## Getting Started

1. Launch Visual Studio Code;
2. Click on <ins>File</ins> > <ins>Open folder</ins> > `<project_name>`;
3. When prompted, re-open the project in a <ins>devcontainer</ins>;
4. When successfully connected to the <ins>devcontainer</ins>, verify that the 
`/scripts/nwpublishers/nwpublisher.py` script contains the correct `project_name`;
5. In the `/scripts/nwpublishers/` folder, paste the following two files:

    ```
    PYPI_API_KEY.txt
    TESTPYPI_API_KEY.txt
    ```

6. Still in the `/scripts/nwpublishers/` folder, add or update the `README.md` file, which will show up on TestPyPi and PyPi once the upload of the package will be successful;
7. Verify that `/src/setup.py` is present and that `/src/setupinfo.py` contains the expected `PROJECT_VERSION`;
8. Once you are confident and ready to publish, click on <ins>Terminal</ins> > <ins>New Terminal</ins> and type the following command (replace `{project_name}` before running it):
    
    ```bash
    python3 /workspaces/{project_name}/scripts/nwpublishers/nwpublisher.py --enable_testpypi
    ```
	
	```bash
	python3 /workspaces/{project_name}/scripts/nwpublishers/nwpublisher.py --enable_pypi
	```
	
9. Done!

Regarding `PROJECT_VERSION`, please know that if the publishing process is successful but then you remove the package from the package index, you won't be able anymore to re-use that specific `PROJECT_VERSION`.

A more convenient alternative to run `nwpublishers` is to add the commands to `tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
	
        ...

        // nwpublishers
		
        {
            "label": "nwpublishers: TestPyPI",
            "type": "shell",
            "command": "python3 ${workspaceFolder}/scripts/nwpublishers/nwpublisher.py --enable_testpypi",
            "problemMatcher": []
        },
        {
            "label": "nwpublishers: PyPI",
            "type": "shell",
            "command": "python3 ${workspaceFolder}/scripts/nwpublishers/nwpublisher.py --enable_pypi",
            "problemMatcher": []
        }
	]
}
```

## Dependencies

The `nwpublisher.py` script depends upon `build` and `twine` in order to run:

```bash
root@bcf485fc84e4:/# pip show build
Name: build
Version: 1.6.1

root@bcf485fc84e4:/# pip show twine
Name: twine
Version: 7.0.0
```

Please make sure to add them to the <ins>devcontainer</ins> using the following command:

```bash
python3 -m pip install --upgrade build twine
```

```dockerfile
# NWPUBLISHERS
RUN pip install build==1.6.1 
RUN pip install twine==7.0.0
```

## How-To Verify A Package

On Debian (but the procedure is similar on Windows or Mac), you are able to verify that package installs as expected by running the following commands in a terminal (replace `{project_name}` before running them):

```bash
sudo apt install python3.12-venv
python3 -m venv /tmp/{project_name}
source /tmp/{project_name}/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple {project_name}
deactivate
rm -rf /tmp/{project_name}
```

If you want to use PyPI instead of TestPyPI, remove `--index-url https://test.pypi.org/simple/` and `--extra-index-url https://pypi.org/simple`.

## PyPI Statistics

By default, PyPI doesn't expose package downloads. 

To overcome the issue, there are these two third-party websites:

- Latest six months of data: [PyPiStats](https://pypistats.org/)
- All historical data: [Pepy Tech](https://pepy.tech/)

## Long Description

In order to work for publishing on TestPyPI / PyPI, the `setup.py` file must contain the following two fields:

- `long_description`, which contains the text displayed on your TestPyPI / PyPI release page. 
- `long_description_content_type`, which tells how TestPyPI / PyPI should render the text in the release page (`text/markdown`, `text/x-rst` and `text/plain`).

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)