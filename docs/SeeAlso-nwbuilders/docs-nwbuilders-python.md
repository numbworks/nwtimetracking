# nwbuilders-python
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-01-02 | numbworks | Created. |
| 2026-04-06 | numbworks | Last update. |

## Introduction

`nwbuilders` is a collection of guidelines and configuration templates that simplify and standardize the cross-compilation and packaging workflow for CLI applications on local build agents.

## Overview

To build Python applications, two approaches will be used:

- `nuitka` for Linux executables (AMD64 and ARM64)
- `pyinstaller` for Windows executables (AMD64)

None of them supports cross-compilation, therefore a build agent for each supported architecture (AMD64 and ARM64) must be provided.

In theory, it's possible to emulate ARM64 on AMD64 by using `nuitka` with QEMU, but in my tests the performances were 8x-14x slower, which means waiting up to 14 hours for an application that takes ~50 min to compile natively on a ARM64 CPU. This possibility has been therefore discarded.

For the Windows AMD64 builds, two options were evaluated for the corresponding build agents:

1. Using a Windows Server-based container. This option was discarded due to its non-free licensing requirements and its very limited community adoption compared to Linux-based alternatives.
2. Using a Windows-based virtual (or physical) machine. This option was discarded because it requires several manual configuration steps and additional per‑project setup.

Considering the two discarded options above, I choose to still use a Linux container as build agent for Windows build, pairing `pyinstaller` with Wine (Windows "emulation" layer). Unfortunately, `nuitka` is unable to build 64-bit executables under Wine (only 32-bit), therefore `pyinstaller` has been adopted. 

Using `pyinstaller` is a trade-off: we accept to "freeze" the application (instead of compiling it, as `nuitka` does), but we get a building and packaging configuration that it's easier to replicate and run.

## The Configurations

Here the content of the `nwbuilder-<cli_name>-linux` configuration (folder):

```
...
nwbuilder-<cli_name>-linux/
├── <project_alias>.md
├── ...
├── ...
├── <cli_name>.py
├── <cli_name>.sh
├── <cli_name>-dockerfile
└── <cli_name>-icon.png
...
```

Here the content of the `nwbuilder-<cli_name>-win` configuration (folder):

```
...
nwbuilder-<cli_name>-linux/
├── ...
├── ...
├── <cli_name>.py
├── <cli_name>.sh
├── <cli_name>-dockerfile
├── <cli_name>-icon.ico
└── ucrtbase.dll
...
```

Each configuration (folder) must contain all the Python files the `<cli_name>.py` may reference  - i.e. `<library_name>.py` and `setupinfo.py`.

Here how every `nwbuilders` configuration (folder) is stored in the target's project repository:

```
...
/docs/
└── SeeAlso-nwbuilders
    └── docs-nwbuilders-python.md
    ...
/scripts/
└── nwbuilders/
    ├── `nwbuilder-<cli_name>-linux`
        ├── ...
    └── `nwbuilder-<cli_name>-win`
        ├── ...
...
```

## The Host Machines

Here a summary of which host machine (physical or virtual) to use for which `nwbuilders` configuration (folder):

|Host CPU|NWBuilder|Artifacts|
|---|---|---|
|ARM64|`nwbuilder-<cli_name>-linux`|`<cli_name>-v<version>-linux-arm64.zip`, `*.deb`|
|AMD64|`nwbuilder-<cli_name>-linux`|`<cli_name>-v<version>-linux-amd64.zip`, `*.deb`|
|AMD64|`nwbuilder-<cli_name>-win`|`<cli_name>-v<version>-win-amd64.zip`|

Here the pre-requisites for every host machine:

- Required CPU architecture (ARM64 on AMD64)
- Linux-based OS
- Docker

All the required software dependencies are defined in the Dockerfile of every `nwbuilders` configuration (folder).

To launch a `nwbuilders` configuration:

1. Copy the `nwbuilders` configuration (folder) to the host machine, including all the required Python files in their most updated revision;
2. Launch the terminal and enter in the `nwbuilders` configuration (folder);
3. Run: `chmod +x <cli_name>.sh`
4. Run: `./<cli_name>.sh`
5. The building process will start and you will find the expected artifacts in the same folder after a while;
6. Done!

## The Artifacts

In the majority of the cases, `nwbuilder-<cli_name>-linux` produces the following artifacts:

1. A ZIP file containing only the executable file
2. A DEB package that, once installed, will provide the executable file, the menu item with the icon and a `man` page

In the majority of the cases, `nwbuilder-<cli_name>-win` produces the following artifact:

1. A ZIP file containing only the executable file (enriched by an icon and by metadata)

In some edge cases, the resulting artifact consists of multiple files rather than a single self‑contained executable.

## Notes About `nwbuilder-<cli_name>-linux`

- `nuitka` compiles your Python modules into optimized C/C++ and then into native machine code, which can improve runtime performance and makes casual source extraction harder than packages created with tools like `pyinstaller`, which primarily package the interpreter and your bytecode with minimal compilation.
- `zstandard` is used by `nuitka` to compress the final executable when the `--onefile` option is selected. Without `zstandard`, `nuitka` will compile the application anyway, but it will skip the compression.
- `patchelf` is used by `nuitka` for the standalone builds. It's an utility that helps executables to find the shared libraries you bundle with them at runtime. 
- On Linux, installing `ccache` increases the speed of the re-compilation processes. `nuitka` translates Python to C++ and `ccache` (C Compiler Cache) acts as a persistent storage for compiled object files. On Windows (Wine), `nuitka` usually handles the C compiler internally (using MinGW) and therefore you don't need to install a Windows version of `ccache`.
- `RUN --mount=type=cache,target=/root/.ccache` stores data in the "Build Cache" rather than the image layers themselves. It exists only during the build phase. Once the image is finished, the contents of that cache are not part of the final image.
- The `--output-dir="/output"` flag is required because `nuitka` fails to compile if the output directory is the same as the directory in which the final executable will be saved.
- The `--include-module` flag is required because `nuitka` does not automatically follow imports of other modules, not even if placed in the same folder. If the flag is not specified, `nuitka` will successfully compile the provided module anyway, but once launched, a `ModuleNotFoundError: No module named '...'` error message will be thrown.
- The `--include-package=charset_normalizer` flag is required because `nuitka` does not automatically import `charset-normalizer`, a dependency for `requests`. If you omit this flag, the following error message will be returned: "_RequestsDependencyWarning: Unable to find acceptable character detection dependency (chardet or charset_normalizer)._".

## Notes About `nwbuilder-<cli_name>-win`

- We download `wine` using winehq's repositories, because at the moment of writing the latest version available on Debian's repositories is Wine 8.0 (very old). Python 3.12 and `nuitka` rely on Windows APIs that Wine 8.0 doesn't fully implement, which causes hard aborts (CopyFile2, VariantToString, ...).
- `WINEDLLOVERRIDES="mscoree,mshtml="` disables Wine's Mono and Gecko integration that are a common cause of freezes when Wine is used in headless mode.
- It’s necessary to wrap every `wine` command with `timeout`, `dbus-run-session` and `wineserver` because otherwise the command can freeze when run inside a container (for three different reasons). `; wineserver -k 2>/dev/null` forcibly shuts down Wine background processes like `services.exe` or  `explorer.exe`, so that the build step finishes deterministically. `|| true` prevents the cleanup from failing the build if `wine` is already stopped.
- `wine reg add "HKCU\\Software\\Wine" /v Version /t REG_SZ /d win10 ...` sets `wine`'s Windows version equal to Windows 10 because the Python 3.12 Windows installer requires Windows 8.1 or later, and by default Wine reports Windows 7, which causes the installer to fail.
- The `echo exit=$?` statements are meant for diagnostic reasons.
- The `export XDG_RUNTIME_DIR=$(mktemp -d)` statement is required to avoid the `XDG_RUNTIME_DIR is not set in the environment` error message.
- `xvfb` and `xauth` allow GUI-dependent Windows installers and applications to run headlessly inside a Docker container.
- `WINEPREFIX=/opt/wine64` forces Wine to use this prefix location instead of `/root/.wine`.`WINEARCH=win64` tells Wine to make this environment a 64-bit Windows setup.
- `ucrtbase.dll` is required by PyInstaller on Wine Wbecause modern Python for Windows requires the Microsoft Universal C Runtime (UCRT), and Wine often ships with an incomplete or outdated implementation of that DLL. When PyInstaller tries to analyze or bundle Python extensions, it ends up loading Windows binaries that depend on the real UCRT and Wine's stub just isn’t good enough.

## Notes About `<cli_name>.sh`

- The `<cli_name>.sh` script runs `docker build` with the `--progress=plain` flag, so that the whole log is shown and not swallowed. This flag makes eventual debug sessions easier.

## Notes About The Debian Packages

- `Exec=/bin/bash -c '/usr/bin/${PROJECT_ALIAS}; exec bash'` will launch the installed CLI application without closing the terminal window afterwards. Bash's full-path is used to increase compatibility.

## Notes About The `man` Pages

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

## Notes about Chromium and `onefile` bundling

As a rule of thumb, if your Python app relies on Chromium, bundling it as `onefile` is not a viable path. Chromium isn't just a single-file dependency, but it’s a massive ecosystem of specialized libraries, sandboxing processes and resource folders. When you force that into a onefile wrapper, you are essentially asking a temporary, compressed environment to manage a high-performance engine. 

When Chromium is necessary, a `standalone` bundling strategy is the correct one to adopt.

## Notes About Maintenance On Host Machines

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

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)