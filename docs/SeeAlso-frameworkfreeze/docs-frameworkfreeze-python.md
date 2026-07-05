# frameworkfreeze-python
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-05-14 | numbworks | Created. |
| 2026-06-28 | numbworks | Last update. |
                                   
## Introduction

A "framework freeze" is a strategy that advocates the usage of the same version of frameworks and dependencies among several projects by creating a reference document. 

The main scope of this strategy is to simplify planned updates by reducing the possible issues and by centralizing their resolution. 

This documents collects all the information regarding the "framework freeze" strategy adopted by all `nw` applications.

# The Current Strategy

At the moment of writing, all `nw` applications developed in Python rely on a devcontainer based upon the `python:3.12.5-bookworm` image, which it's based on `Debian 12` and `Python 3.12.5`.

# The Upcoming Strategy

Considering that Debian is not only the OS I use in all my devcontainers, but also the OS running on all my Linux machines (laptops, servers, handheld, virtual machines,...), it would be an improvement to run the application directly using the default Python intepreter without installing duplicates with funky names - e.g. `python3.13`. Even if Docker is almost always present, it's good to have a "Plan B". 

Additionally, adopting the default Python interpreter ensures that my applications are fully compatible with the underlying C libraries (libc, OpenSSL) provided by the given Debian release.

For this reason, the upcoming "framework freeze" strategy will aim to adopt the same Python version shipped in a Debian major release - e.g. `Debian 13` + `Python 3.13`:

| Debian Version | Debian Release | Debian EOL | Python Version | Python Release | Python EOL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| - | - | - | *3.15* | *~ Oct 2026* | *~ Oct 2031* |
| *Forky (14)* | *~ Aug 2027*| *~ Aug 2030* | *3.14* | *Oct 2025* | *Oct 2030* |
| <u>Trixie (13)</u> | <u>Aug 2025</u> | <u>Aug 2028</u> | <u>3.13</u> | <u>Oct 2023</u> | <u>Oct 2028</u> |
| - | - | - | *3.12* | *Oct 2023* | *Oct 2028* |

**Debian EOL** refers to the point at which a Debian release reaches the end of its regular support period (typically three years after its initial release), while **Python EOL** marks the end of the five‑year support window for a given Python version.

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)