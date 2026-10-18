# nwbuilders-python
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-01-02 | numbworks | Created. |
| 2026-07-27 | numbworks | Last update. |

## Introduction

`nwbuilders` is a collection of guidelines and configuration templates that simplify and standardize the cross-compilation and packaging workflow for CLI applications on local build agents.

## Target Architectures

We target the following operating systems and architectures:

- Debian Linux installers (AMD64 and ARM64)
- Generic Linux executables (AMD64 and ARM64)
- Windows executables (AMD64)

**Disclaimer**: as an open‑source developer, I intentionally and firmly chose not to target Apple's MacOS.

The reasons are:

- <u>Paid certification</u>: distributing binaries requires an annual developer license, which is incompatible with free software distribution.
- <u>Expensive hardware</u>: building and testing MacOS apps requires proprietary Apple hardware with a high entry cost and a closed ecosystem.
- <u>Lack of open‑source investment</u>: Apple is not among the companies that actively support open‑source projects with funding or engineering resources.
- <u>No local cross‑compilation</u>: Python applications cannot be cross‑compiled for MacOS from Linux or Windows, breaking my unified build workflow.

If you are a MacOS user, you can still attempt to compile or run my applications from the source code.

## Application Packaging Tools

To build Python applications, two packaging tools are available (`nuitka` and `pyinstaller`) but none of them supports cross-compilation, therefore a build agent for each supported architecture (AMD64 and ARM64) must be provided.

We adopt two separate approaches:

- `nuitka` running in a Linux container on x64 and ARM host machines to build Linux executables (AMD64 and ARM64).
- `pyinstaller` running in a Linux container and in a Wine environment to build Windows executables (AMD64).

The following approaches have been evaluated and discarded:

1. <u>ARM64 emulation on AMD64</u>. It's possible to emulate ARM64 on AMD64 by using `nuitka` with QEMU, but in my tests the performances were 8x-14x slower, which means waiting up to 14 hours for compiling an application that takes ~50 min to compile natively on a ARM64 CPU. This possibility has been therefore discarded.
2. <u>Windows Server-based containers</u>. This option was discarded due to its non-free licensing requirements and its very limited community adoption compared to Linux-based alternatives.
3. <u>A Windows-based virtual (or physical) machine</u>. This option was discarded because it requires several manual configuration steps and additional per‑project setup.
4. <u>Nuitka in a Wine environment</u>. Unfortunately, `nuitka` is unable to build 64-bit executables under Wine (only 32-bit). Therefore `pyinstaller` has been adopted as a trade-off (we accept to "freeze" the application instead of compiling it, as `nuitka` does).

## Project Structure And File Roles

An example of the project structure:

```
...
/scripts/
└── nwbuilders/
    ├── nwbuilder-nwtimetrackingcli-linux
        ├── nwtime.md
        ├── {nwtimetracking.py}
        ├── {nwtimetrackingcli.py}
        ├── nwtimetrackingcli.sh
        ├── nwtimetrackingcli-dockerfile
        ├── nwtimetrackingcli-icon.png
        ├── {setup.py}
        └── {setupinfo.py}
    └── nwbuilder-nwtimetrackingcli-win
        ├── {nwtimetracking.py}
        ├── {nwtimetrackingcli.py}
        ├── nwtimetrackingcli.sh
        ├── nwtimetrackingcli-dockerfile
        ├── nwtimetrackingcli-icon.ico
        ├── {setup.py}
        ├── {setupinfo.py}
        └── ucrtbase.dll
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
|`nwbuilder-nwtimetrackingcli-linux`|This folder must be moved to the AMD64 and ARM64 build machines.|
|`nwbuilder-nwtimetrackingcli-win`|This folder must be moved to the AMD64 build machine.|
|`nwtime.md`|This is the source file for the `man` entry installed with the Debian packages.|
|`nwtimetrackingcli.sh`|This script launches the build environment that produces the CLI executables and the Debian packages.|
|`nwtimetrackingcli-dockerfile`|This is the build environment, where all the required Python dependencies must be listed.|
|`nwtimetrackingcli-icon.png`|This is the icon file for the Linux executable.|
|`nwtimetrackingcli-icon.ico`|This is the icon file for the Windows executable.|
|`ucrtbase.dll`|This is a Windows library required by Wine to enable PyInstaller to create the Windows executable.|
|`setup.py`|This contains the building instructions for the `pip` package.|
|`setupinfo.py`|This contains the key information about the application (name, version, description).|
|`.gitattributes`|This enforces LF end‑of‑line formatting for Linux‑sensitive files (such as `*.sh` and `man` source files).|

Side note: the files between curly brackets are supposed to be only on the build machines, therefore we can avoid to duplicate them in the repository.

## The GitAttributes File

The `.gitattributes` file must include the following lines (replace the `md` file as needed):

```
...
# Force LF for EOL‑sensitive files (CRLF breaks them on Linux)
*.sh text eol=lf
nwtime.md text eol=lf
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

## The Host Machines

For this build pipeline, two separate host machines (physical or virtual) are required: 

|Machine Id|Host CPU|NWBuilder|Artifacts|
|---|---|---|---|
|1|ARM64|`nwbuilder-<cli_name>-linux`|`<cli_name>-v<version>-linux-arm64.zip`, `*.deb`|
|2|AMD64|`nwbuilder-<cli_name>-linux`|`<cli_name>-v<version>-linux-amd64.zip`, `*.deb`|
|2|AMD64|`nwbuilder-<cli_name>-win`|`<cli_name>-v<version>-win-amd64.zip`|

Both host machines must run a Linux-based OS, have Docker installed and are required to be connected to internet (at least the first time).

To trigger the build pipeline:

1. Copy the `nwbuilders` configuration (folder) to the host machine, including all the required Python files in their most updated revision.
2. Launch the terminal and enter in the `nwbuilders` configuration (folder).
3. Run: `chmod +x <cli_name>.sh`
4. Run: `./<cli_name>.sh`
5. The building process will start and you will find the expected artifacts in the same folder after a while;
6. Done!

## The Artifacts

An example of the expected artifacts generated by the build pipeline:

|Artifact|Description|
|---|---|
|`nwngram-v4.2.1-linux-amd64.deb`|Debian installer for AMD64.|
|`nwngram-v4.2.1-linux-amd64.zip`|Generic Linux executable for AMD64.|
|`nwngram-v4.2.1-linux-arm64.deb`|Debian installer for ARM64.|
|`nwngram-v4.2.1-linux-arm64.zip`|Generic Linux executable for ARM64.|
|`nwngram-v4.2.1-win64.zip`|Windows executable for AMD64.|

Additional information:

1. Each ZIP package contains only the executable. The Windows variant will be supplemented with an application icon and embedded metadata.
2. The DEB packages, once installed, will provide the executable file, the menu item with the icon and a `man` page.
3. In some edge cases, the resulting artifact consists of multiple files rather than a single self‑contained executable.

## The Building Instructions

The building instructions are encapsulated in the following files. The version number and the referenced documentation files need to be updated before each new release. The Dockerfile-based building environments need to be customized when new dependencies are added.

`setup.py`:

```python
'''Contains packaging instructions.'''

# GLOBAL MODULES
from setupinfo import CLI_NAME, PROJECT_VERSION, PROJECT_AUTHOR, PROJECT_URL, LIBRARY_NAME, LIBRARY_DESCRIPTION
from setuptools import setup

# SETUP
if __name__ == "__main__":
    setup(
        name = LIBRARY_NAME,
        version = PROJECT_VERSION,
        description = LIBRARY_DESCRIPTION,
        author = PROJECT_AUTHOR,
        url = PROJECT_URL,
        py_modules = [ LIBRARY_NAME, CLI_NAME, "setupinfo" ],
        install_requires = [ 
            "numpy>=1.26.4",
            "pyarrow>=17.0.0",
            "openpyxl>=3.1.5",
            "pandas>=2.1.4",
            "requests>=2.32.3",
            "matplotlib>=3.9.2",        
            "tabulate>=0.9.0",
            "sparklines>=0.5.0",
            "weasyprint>=66.0",
            "ipython==7.23.1",
            "jinja2==3.1.6"
        ],
        python_requires = ">=3.12",
        license = "MIT",
        entry_points = {
            'console_scripts': [
                f'{CLI_NAME} = {CLI_NAME}:main',
            ],
        }
    )
```

`setupinfo.py`:

```python
'''Contains project information.'''

# INFORMATION
PROJECT_VERSION : str = "6.0.1"
PROJECT_AUTHOR : str = "numbworks"
PROJECT_ALIAS : str = "nwtime"

LIBRARY_NAME : str = "nwtimetracking"
LIBRARY_DESCRIPTION : str = "A library that can run several automated data analysis tasks on a time tracking file and save the results as a PDF report. It's designed to facilitate and gamify a continuous learning journey."

CLI_NAME : str = "nwtimetrackingcli"
CLI_DESCRIPTION : str = "A CLI application that can run several automated data analysis tasks on a time tracking file and save the results as a PDF report. It's designed to facilitate and gamify a continuous learning journey."

PROJECT_URL : str = f"https://github.com/{PROJECT_AUTHOR}/{LIBRARY_NAME}"
```

`nwtimetrackingcli.sh`:

```bash
#!/bin/bash

# --- CONFIGURATION ---
PROJECT_NAME="nwtimetracking"
PROJECT_VERSION="6.0.1"
PROJECT_ALIAS="nwtime"
CLI_NAME="nwtimetrackingcli"

COMPANY_NAME="numbworks"
COPYRIGHT="numbworks"
TRADEMARK="numbworks"
FILE_DESCRIPTION="A CLI application that can run several automated data analysis tasks on a time tracking file and save the results as a PDF report."

DOCKER_FILE="nwtimetrackingcli-dockerfile"
BASE_IMAGE="python:3.12.5-bookworm"

# --- DOCKER IMAGE CHECK ---
if [[ "$(docker images -q $BASE_IMAGE 2> /dev/null)" == "" ]]; then
    docker pull $BASE_IMAGE
fi

# --- BUILD COMMAND ---
time DOCKER_BUILDKIT=1 docker build --progress=plain \
  -f "$DOCKER_FILE" \
  --build-arg PROJECT_NAME="$PROJECT_NAME" \
  --build-arg PROJECT_VERSION="$PROJECT_VERSION" \
  --build-arg PROJECT_ALIAS="$PROJECT_ALIAS" \
  --build-arg CLI_NAME="$CLI_NAME" \
  --build-arg COMPANY_NAME="$COMPANY_NAME" \
  --build-arg COPYRIGHT="$COPYRIGHT" \
  --build-arg TRADEMARK="$TRADEMARK" \
  --build-arg FILE_DESCRIPTION="$FILE_DESCRIPTION" \
  --output . .
```

`nwbuilder-nwtimetrackingcli-linux/nwtimetrackingcli-dockerfile`:

```Dockerfile
FROM python:3.12.5-bookworm AS builder

# --- NWBUILDER ENVIRONMENT --- #
RUN pip install --upgrade pip==26.0.1

RUN apt update; \
    apt -y upgrade; \
    apt -y install build-essential=12.9; \
    apt -y install python3-dev=3.11.2-1+b1; \
    apt -y install python3-pip=23.0.1+dfsg-1; \
    apt -y install patchelf=0.14.3-1+b1; \
    apt -y install ccache=4.8+really4.7.5-1; \
    apt -y install zip=3.0-13; \
	apt -y install go-md2man; \
    pip install nuitka==2.8.9 zstandard==0.25.0


# --- PROJECT DEPENDENCIES --- #
RUN pip install numpy==1.26.4
RUN pip install pyarrow==23.0.0
RUN pip install openpyxl==3.1.5
RUN pip install pandas==2.1.4
RUN pip install requests==2.32.3
RUN pip install matplotlib==3.9.2
RUN pip install tabulate==0.9.0
RUN pip install sparklines==0.5.0
RUN pip install weasyprint==66.0
RUN pip install ipython==7.23.1
RUN pip install jinja2==3.1.6


# --- NWBUILDER COMMAND --- #
COPY . /workspace
WORKDIR /workspace

ARG PROJECT_NAME
ARG PROJECT_VERSION
ARG PROJECT_ALIAS
ARG CLI_NAME
ARG COMPANY_NAME
ARG COPYRIGHT
ARG TRADEMARK
ARG FILE_DESCRIPTION

ENV CCACHE_DIR=/root/.ccache
RUN --mount=type=cache,target=/root/.ccache \
	RAW_ARCH=$(uname -m) && \
    if [ "$RAW_ARCH" = "x86_64" ]; then ARCH="amd64"; \
    elif [ "$RAW_ARCH" = "aarch64" ]; then ARCH="arm64"; \
    else ARCH="$RAW_ARCH"; \
    fi && \
    ZIP_NAME="${PROJECT_ALIAS}-v${PROJECT_VERSION}-linux-${ARCH}" && \
    python3 -m nuitka \
        --jobs=$(nproc) \
        --mode=onefile \
        --output-dir="/output" \
        --output-filename="${PROJECT_ALIAS}" \
        --include-module=${PROJECT_NAME} \
        --assume-yes-for-downloads \
		--noinclude-unittest-mode=nofollow \
		--noinclude-pytest-mode=nofollow \
		--nofollow-import-to=IPython \
		--nofollow-import-to=IPython.* \
		--nofollow-import-to=matplotlib \
		--nofollow-import-to=matplotlib.* \
		--include-package=jinja2 \
		--include-package=pandas \
		--include-package=pyarrow \
		--include-package=openpyxl \
		--include-package=weasyprint \
        --include-package=tabulate \
        --include-package=sparklines \
        --include-package=charset_normalizer \
        --lto=no \
        "${CLI_NAME}.py" && \
    cd /output && \
    zip -9 -j "${ZIP_NAME}.zip" "${PROJECT_ALIAS}" && \
    STAGE=$(mktemp -d "/tmp/${PROJECT_ALIAS}.XXXXXX") && \
    mkdir -p "$STAGE/DEBIAN" "$STAGE/usr/bin" "$STAGE/usr/share/pixmaps" "$STAGE/usr/share/applications" && \
    cp "/output/${PROJECT_ALIAS}" "$STAGE/usr/bin/${PROJECT_ALIAS}" && \
    chmod 0755 "$STAGE/usr/bin/${PROJECT_ALIAS}" && \
    cp "/workspace/${CLI_NAME}-icon.png" "$STAGE/usr/share/pixmaps/${PROJECT_ALIAS}.png" && \
    printf "[Desktop Entry]\nName=${PROJECT_ALIAS}\nExec=/bin/bash -c '/usr/bin/${PROJECT_ALIAS}; exec bash'\nIcon=${PROJECT_ALIAS}\nType=Application\nCategories=Utility;\nTerminal=true\n" > "$STAGE/usr/share/applications/${PROJECT_ALIAS}.desktop" && \
    printf "Package: ${PROJECT_ALIAS}\nVersion: ${PROJECT_VERSION}\nSection: utils\nPriority: optional\nArchitecture: ${ARCH}\nMaintainer: ${COMPANY_NAME}\nDescription: ${FILE_DESCRIPTION}\n" > "$STAGE/DEBIAN/control" && \   
	mkdir -p "$STAGE/usr/share/man/man1" && \
    go-md2man -in "/workspace/${PROJECT_ALIAS}.md" -out "$STAGE/usr/share/man/man1/${PROJECT_ALIAS}.1" && \
    gzip -n9 "$STAGE/usr/share/man/man1/${PROJECT_ALIAS}.1" && \
	dpkg-deb --build --root-owner-group "$STAGE" "/output/${ZIP_NAME}.deb" && \
    rm -rf "$STAGE"


# --- NWBUILDER EXPORT --- #
FROM scratch AS exporter
COPY --from=builder /output/*.zip / 
COPY --from=builder /output/*.deb / 
```

`nwbuilder-nwtimetrackingcli-win/nwtimetrackingcli-dockerfile`:

```Dockerfile
FROM python:3.12.5-bookworm AS builder

# --- NWBUILDER ENVIRONMENT --- #
RUN pip install --upgrade pip==26.0.1

RUN dpkg --add-architecture i386 && \
    apt -y update; \
    apt -y install wget=1.21.3-1+deb12u1; \
    apt -y install cabextract=1.9-3; \
    apt -y install unzip=6.0-28; \
    apt -y install xvfb=2:21.1.7-3+deb12u11; \
    apt -y install xauth=1:1.1.2-1; \
    apt -y install p7zip-full=16.02+dfsg-8; \
    apt -y install zip=3.0-13; \
    mkdir -p /etc/apt/keyrings; \
    wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key; \
    wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/debian/dists/bookworm/winehq-bookworm.sources; \
    apt update; \
    apt -y install winehq-stable=11.0.0.0~bookworm-1; \
    apt -y install wine-stable=11.0.0.0~bookworm-1; \
    apt -y install wine-stable-amd64=11.0.0.0~bookworm-1; \
    apt -y install wine-stable-i386=11.0.0.0~bookworm-1

RUN wget https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe -O /home/python-3.12.5-amd64.exe

ENV WINEPREFIX=/opt/wine64 \
    WINEARCH=win64 \
    WINEDLLOVERRIDES="ucrtbase=n,b;mscoree,mshtml=" \
    WINEDEBUG=-all \
    WINEDEBUGGER=/bin/true

RUN mkdir -p /opt/wine64

RUN timeout 300s dbus-run-session -- xvfb-run -a sh -lc \
        'wineboot -u' \
    ; wineserver -k 2>/dev/null || true

RUN timeout 30s dbus-run-session -- xvfb-run -a sh -lc \
        'wine reg add "HKCU\\Software\\Wine" /v Version /t REG_SZ /d win10 /f; echo exit=$?' \
    ; wineserver -k 2>/dev/null || true

RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc \
    'wine /home/python-3.12.5-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir="C:\\Python312" /log "C:\\python-install.log"' \
    ; wineserver -k 2>/dev/null || true

RUN timeout 300s dbus-run-session -- xvfb-run -a sh -lc \
    'ls -la "$WINEPREFIX/drive_c/Python312" || true; \
     test -f "$WINEPREFIX/drive_c/Python312/python.exe"; \
     wine C:\\Python312\\python.exe --version'

RUN timeout 120s dbus-run-session -- xvfb-run -a sh -lc \
     'wine C:\\Python312\\python.exe -m ensurepip --upgrade; echo exit=$?' \
 ; wineserver -k 2>/dev/null || true

RUN timeout 900s dbus-run-session -- xvfb-run -a sh -lc \
     'wine C:\\Python312\\python.exe -m pip install --upgrade pip==26.0.1 wheel==0.45.1 setuptools==80.9.0 pyinstaller==6.11.1' \
 ; wineserver -k 2>/dev/null || true

RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc \
     'wine C:\\Python312\\python.exe -m pip install "https://github.com/numbworks/nwversioninfofiles/archive/refs/tags/v2.0.0.zip#subdirectory=src"; echo exit=$?' \
 ; wineserver -k 2>/dev/null || true

COPY ucrtbase.dll /home/ucrtbase.dll
RUN cp -f /home/ucrtbase.dll /opt/wine64/drive_c/windows/system32/ucrtbase.dll


# --- PROJECT DEPENDENCIES --- #
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install numpy==1.26.4; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install pyarrow==23.0.0; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install openpyxl==3.1.5; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install pandas==2.1.4; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install requests==2.32.3; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install matplotlib==3.9.2; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install tabulate==0.9.0; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install sparklines==0.5.0; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install weasyprint==66.0; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install ipython==7.23.1; echo exit=$?'; wineserver -k 2>/dev/null || true
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc 'wine C:\\Python312\\python.exe -m pip install jinja2==3.1.6; echo exit=$?'; wineserver -k 2>/dev/null || true

RUN wget -O /home/gtk3-runtime.exe \
    https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe

RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc \
     'wine /home/gtk3-runtime.exe /S' \
 ; wineserver -k 2>/dev/null || true
 

# --- NWBUILDER COMMAND --- #
COPY . /workspace
WORKDIR /workspace

ARG PROJECT_NAME
ARG PROJECT_VERSION
ARG PROJECT_ALIAS
ARG CLI_NAME
ARG COMPANY_NAME
ARG COPYRIGHT
ARG TRADEMARK
ARG FILE_DESCRIPTION

RUN FILENAME="${PROJECT_ALIAS}-v${PROJECT_VERSION}-win64" && \
    TMPDIR="/tmp/pyinstaller" && \
    VERSION_FILE="${TMPDIR}/version_info.txt" && \
    ROOT_DIR="/workspace" && \
    mkdir -p "${TMPDIR}" "/output" && \
    cp "/workspace/${CLI_NAME}-icon.ico" "${TMPDIR}/icon.ico" && \
    export XDG_RUNTIME_DIR=$(mktemp -d) && \
    CHECK_OUTPUT=$(export PYTHONPATH="${ROOT_DIR}"; wine C:\\Python312\\python.exe -c "import ${CLI_NAME}" 2>&1) || (echo "$CHECK_OUTPUT" && exit 1) && \
    output=$(wine C:\\Python312\\python.exe -m nwversioninfofilescli \
        --company_name "${COMPANY_NAME}" \
        --file_description "${FILE_DESCRIPTION}" \
        --file_version "${PROJECT_VERSION}" \
        --legal_copyright "${COPYRIGHT}" \
        --original_filename "${PROJECT_ALIAS}.exe" \
        --product_name "${PROJECT_NAME}" \
        --verify \
        --output_path "${VERSION_FILE}" 2>&1) || (echo "$output" && exit 1) && \
    WIN_ROOT_DIR="$(winepath -w "${ROOT_DIR}")" && \
    WIN_ENTRY="${WIN_ROOT_DIR}\\${CLI_NAME}.py" && \
    WIN_ICON="$(winepath -w "${TMPDIR}/icon.ico")" && \
    WIN_DIST="$(winepath -w "/output")" && \
    WIN_VER_FILE="$(winepath -w "${VERSION_FILE}")" && \
    timeout 36000s dbus-run-session -- xvfb-run -a sh -lc "\
        wine C:\\\\Python312\\\\python.exe -m PyInstaller \
            --noconfirm \
			--onefile \
            --name '${PROJECT_ALIAS}' \
            --icon '${WIN_ICON}' \
            --version-file '${WIN_VER_FILE}' \
            --distpath '${WIN_DIST}' \
            --workpath '$(winepath -w "${TMPDIR}/work")' \
            --specpath '$(winepath -w "${TMPDIR}/spec")' \
            --exclude-module IPython \
            --exclude-module matplotlib \
            --exclude-module pkg_resources \
            --hidden-import ${PROJECT_NAME} \
            --hidden-import openpyxl \
            --hidden-import tabulate \
            --hidden-import sparklines \
			--collect-all jinja2 \
            --collect-all numpy \
            --collect-all pandas \
			--collect-all pyarrow \
            --collect-all weasyprint \
            --collect-submodules=charset_normalizer \
            --collect-binaries cairocffi \
            --collect-binaries cffi \
            --collect-binaries weasyprint \
			--add-binary \"C:\\Program Files\\GTK3-Runtime Win64\\bin\\libgobject-2.0-0.dll;.\" \
			--add-binary \"C:\\Program Files\\GTK3-Runtime Win64\\bin\\libglib-2.0-0.dll;.\" \
			--add-binary \"C:\\Program Files\\GTK3-Runtime Win64\\bin\\libgio-2.0-0.dll;.\" \
			--add-binary \"C:\\Program Files\\GTK3-Runtime Win64\\bin\\libpango-1.0-0.dll;.\" \
			--add-binary \"C:\\Program Files\\GTK3-Runtime Win64\\bin\\libpangocairo-1.0-0.dll;.\" \
			--add-binary \"C:\\Program Files\\GTK3-Runtime Win64\\bin\\libcairo-2.dll;.\" \
            '${WIN_ENTRY}' \
    " && \
    zip -9 -j "/output/${FILENAME}.zip" "/output/${PROJECT_ALIAS}.exe" && \
    rm -f "/output/${PROJECT_ALIAS}.exe"


# --- NWBUILDER EXPORT --- #
FROM scratch AS exporter
COPY --from=builder /output/*.zip / 
```

## The Publishing Strategies

The artifacts generated by the build pipeline are manually attached to the Github release.

No automatic publishing available at the moment.

## The Debian Packages

`Exec=/bin/bash -c '/usr/bin/${PROJECT_ALIAS}; exec bash'` will launch the installed CLI application without closing the terminal window afterwards. Bash's full-path is used to increase compatibility.

## The Man Page

Let's say that the source file for the `man` page is called `nwxxx.md`.

To build and preview the `man` page:

```bash
go-md2man -in nwxxx.md -out nwxxx.1
man ./nwxxx.1
```

The preview doesn't show the man page with 100% accuracy, therefore you need to install the `deb` package and run `man nwxxx`. Please know that you can't use the devcontainer for this, but you require a real Linux machine. 

If you try, you'll get the following error messages:

```bash
$ man nwxxx
No manual entry for nwxxx

$ ls -l /usr/share/man/man1/nwxxx.1.gz
ls: cannot access '/usr/share/man/man1/nwxxx.1.gz': No such file or directory 
```

The reason is that the devcontainer is a slimmed-down Linux environment and it has a "No Documentation" policy active. This means that a system-level filter is intercepting the installation and deleting documentation to save disk space. 

You can verify it by typing the following command:

```bash
$ nano /etc/dpkg/dpkg.cfg.d/docker
```

```
...
path-exclude /usr/share/man/*
....
```

Side note: the Markdown file used for `go-md2man` must have LF as end-of-line.

## Notes: `<cli_name>.sh`

- The `<cli_name>.sh` script runs `docker build` with the `--progress=plain` flag, so that the whole log is shown and not swallowed. This flag makes eventual debug sessions easier.

## Notes: `nwbuilder-<cli_name>-linux`

- `nuitka` compiles your Python modules into optimized C/C++ and then into native machine code, which can improve runtime performance and makes casual source extraction harder than packages created with tools like `pyinstaller`, which primarily package the interpreter and your bytecode with minimal compilation.
- `zstandard` is used by `nuitka` to compress the final executable when the `--onefile` option is selected. Without `zstandard`, `nuitka` will compile the application anyway, but it will skip the compression.
- `patchelf` is used by `nuitka` for the standalone builds. It's an utility that helps executables to find the shared libraries you bundle with them at runtime. 
- On Linux, installing `ccache` increases the speed of the re-compilation processes. `nuitka` translates Python to C++ and `ccache` (C Compiler Cache) acts as a persistent storage for compiled object files. On Windows (Wine), `nuitka` usually handles the C compiler internally (using MinGW) and therefore you don't need to install a Windows version of `ccache`.
- `RUN --mount=type=cache,target=/root/.ccache` stores data in the "Build Cache" rather than the image layers themselves. It exists only during the build phase. Once the image is finished, the contents of that cache are not part of the final image.
- The `--output-dir="/output"` flag is required because `nuitka` fails to compile if the output directory is the same as the directory in which the final executable will be saved.
- The `--include-module` flag is required because `nuitka` does not automatically follow imports of other modules, not even if placed in the same folder. If the flag is not specified, `nuitka` will successfully compile the provided module anyway, but once launched, a `ModuleNotFoundError: No module named '...'` error message will be thrown.
- The `--include-package=charset_normalizer` flag is required because `nuitka` does not automatically import `charset-normalizer`, a dependency for `requests`. If you omit this flag, the following error message will be returned: "_RequestsDependencyWarning: Unable to find acceptable character detection dependency (chardet or charset_normalizer)._".

## Notes: `nwbuilder-<cli_name>-win`

- We download `wine` using winehq's repositories, because at the moment of writing the latest version available on Debian's repositories is Wine 8.0 (very old). Python 3.12 and `nuitka` rely on Windows APIs that Wine 8.0 doesn't fully implement, which causes hard aborts (CopyFile2, VariantToString, ...).
- `WINEDLLOVERRIDES="mscoree,mshtml="` disables Wine's Mono and Gecko integration that are a common cause of freezes when Wine is used in headless mode.
- It’s necessary to wrap every `wine` command with `timeout`, `dbus-run-session` and `wineserver` because otherwise the command can freeze when run inside a container (for three different reasons). `; wineserver -k 2>/dev/null` forcibly shuts down Wine background processes like `services.exe` or  `explorer.exe`, so that the build step finishes deterministically. `|| true` prevents the cleanup from failing the build if `wine` is already stopped.
- `wine reg add "HKCU\\Software\\Wine" /v Version /t REG_SZ /d win10 ...` sets `wine`'s Windows version equal to Windows 10 because the Python 3.12 Windows installer requires Windows 8.1 or later, and by default Wine reports Windows 7, which causes the installer to fail.
- The `echo exit=$?` statements are meant for diagnostic reasons.
- The `export XDG_RUNTIME_DIR=$(mktemp -d)` statement is required to avoid the `XDG_RUNTIME_DIR is not set in the environment` error message.
- `xvfb` and `xauth` allow GUI-dependent Windows installers and applications to run headlessly inside a Docker container.
- `WINEPREFIX=/opt/wine64` forces Wine to use this prefix location instead of `/root/.wine`.`WINEARCH=win64` tells Wine to make this environment a 64-bit Windows setup.
- `ucrtbase.dll` is required by PyInstaller on Wine Wbecause modern Python for Windows requires the Microsoft Universal C Runtime (UCRT), and Wine often ships with an incomplete or outdated implementation of that DLL. When PyInstaller tries to analyze or bundle Python extensions, it ends up loading Windows binaries that depend on the real UCRT and Wine's stub just isn’t good enough.

## Notes: Chromium And Onefile Bundling

As a rule of thumb, if your Python app relies on Chromium, bundling it as `onefile` is not a viable path. Chromium isn't just a single-file dependency, but it’s a massive ecosystem of specialized libraries, sandboxing processes and resource folders. When you force that into a onefile wrapper, you are essentially asking a temporary, compressed environment to manage a high-performance engine. 

When Chromium is necessary, a `standalone` bundling strategy is the correct one to adopt.

## Notes: Maintenance On Host Machines

The `nwbuilders` configurations (folders) rely heavily on the Docker's "Build Cache" mechanism. Without regular maintenance, this cache can grow quickly and consume a significant amount of disk space on the host machine.

To get a high-level overview of how much space images and build caches are consuming:

```
$ docker system df
```

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          2         1         1.013GB   1.013GB (99%)
Containers      1         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     160       0         20.11GB   20.11GB
```

To delete all the items in "Build Cache":

```
docker builder prune 
```

To delete all the items in "Build Cache" and in "Images":

```
docker builder prune -a
```

## Notes: `nwversioninfofiles`

In the Dockerfile for `nwbuilder-<cli_name>-win`, the "utility version" of `nwversioninfofiles` has been renamed, because the "to-be-compiled version" of `nwversioninfofiles` was creating a recursion:

```
...
RUN timeout 1800s dbus-run-session -- xvfb-run -a sh -lc \
     'wine cmd /c ren C:\\Python312\\Lib\\site-packages\\nwversioninfofiles.py nwversioninfofiles_v1.py; echo exit=$?' \
 ; wineserver -k 2>/dev/null || true
 
...
output=$(wine C:\\Python312\\python.exe -m nwversioninfofiles_v1 \
...
```

This is the recursion-related error message:

```
...
#21 64.28   File "C:\Python312\Lib\site-packages\PyInstaller\building\api.py", line 620, in __init__
#21 64.28     self.versrsrc = versioninfo.load_version_info_from_text_file(self.versrsrc)
#21 64.28                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#21 64.28   File "C:\Python312\Lib\site-packages\PyInstaller\utils\win32\versioninfo.py", line 568, in load_version_info_from_text_file
#21 64.28     with open(filename, 'rb') as fp:
#21 64.28          ^^^^^^^^^^^^^^^^^^^^
#21 64.28 FileNotFoundError: [Errno 2] No such file or directory: 'Z:\\tmp\\pyinstaller\\version_info.txt'
...
```

## Notes: `pyinstaller` and `setuptools`

The first of these two flags:

```
...
--noinclude-setuptools-mode=nofollow \
--include-package=PyInstaller \
...
```

is provided because `PyInstaller` depends upon `setuptools`:

```
...
#11 0.880 Nuitka-Options: Used command line options:
#11 0.880 Nuitka-Options:   --jobs=4 --mode=onefile --output-dir=/output --output-filename=nwvinf --include-module=nwversioninfofiles --assume-yes-for-downloads --remove-output --noinclude-unittest-mode=nofollow --noinclude-pytest-mode=nofollow --include-package=PyInstaller --lto=no nwversioninfofilescli.py
#11 2.364 Nuitka: Starting Python compilation with:
#11 2.364 Nuitka:   Version '2.8.9' on Python 3.12 (flavor 'Unknown') commercial grade 'not installed'.
#11 134.1 Nuitka-Plugins:WARNING: anti-bloat: Undesirable import of 'setuptools' in 'PyInstaller.utils.hooks.setuptools' (at '/usr/local/lib/python3.12/site-packages/PyInstaller/utils/hooks/setuptools.py:24') encountered. It may slow down compilation.
#11 134.1 Nuitka-Plugins:WARNING:     Complex topic! More information can be found at https://nuitka.net/info/unwanted-module.html
#11 134.3 Nuitka-Plugins:WARNING: anti-bloat: Undesirable import of 'setuptools' in 'PyInstaller.utils.hooks.setuptools' (at '/usr/local/lib/python3.12/site-packages/PyInstaller/utils/hooks/setuptools.py:82') encountered. It may slow down compilation.
...
```

## Source

The following project is used for the examples in this document:

- [nwtimetracking](https://github.com/numbworks/nwtimetracking)

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)