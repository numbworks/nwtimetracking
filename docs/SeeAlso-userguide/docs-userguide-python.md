# userguide-python
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-07-04 | numbworks | Created. |
| 2026-07-04 | numbworks | Last update. |

## Introduction

This guide collects all the information to get started with a `nw` project as a user.

## Getting Started (as a user)

As a user, there are several methods you can follow to install and run the `nw*` applications: 

1. Downloading and installing the latest binary release from [NW's Software Hub](https://numbworks.github.io/)
2. Downloading and installing the latest release with the `pip install` command provided by [NW's Software Hub](https://numbworks.github.io/)
3. Downloading and installing the latest release with the `pip install` command against the project's repository:

	```
	pip install "https://github.com/numbworks/{application_name}/archive/refs/tags/{version}.zip#subdirectory=src"
	```

	```
	pip install 'git+https://github.com/numbworks/{application_name}.git@{version}#egg={application_name}&subdirectory=src'
	```

4. Cloning the repository using `git` in a `Python` container running on `Docker`:

	```bash
	sudo apt install docker.io
	docker run -it python:3.12.5-bookworm /bin/bash
	git clone https://github.com/numbworks/{application_name}.git
	cd {application_name}/src
	python3 -m pip install -e .
	{application_name}cli
	```

	```powershell
	docker run -it python:3.12.5-bookworm /bin/bash
	git clone https://github.com/numbworks/{application_name}.git
	cd {application_name}/src
	python3 -m pip install -e .
	{application_name}cli
	```

5. (Not recommended) Cloning the repository using `git` and installing the application from the source code using the local `Python` interpreter:

	```bash
	sudo apt install git python3 python3-pip python3.13-venv
	git clone https://github.com/numbworks/{application_name}.git
	cd {application_name}/src
	python3 -m venv .venv
	source .venv/bin/activate
	python3 -m pip install -e .
	{application_name}cli
	deactivate
	```

	```powershell
	git clone https://github.com/numbworks/{application_name}.git
	python.exe -m pip install -e .
	{application_name}cli
	```

Notes:
- When the code block is labeled as `bash`, it refers to a generic Debian 13 environment, while when labeled as `powershell`, it refers to Windows environment.
- Using the local `Python` interpreter is not recommended on Debian-based distributions, because it can be cumbersome due to the need for virtual environments and the risk of interpreter mismatches.

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)