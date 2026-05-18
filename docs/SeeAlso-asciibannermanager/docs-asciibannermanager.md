# asciibannermanager
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-05-07 | numbworks | Created. |
| 2026-05-07 | numbworks | Last update. |

## Introduction

The `AsciiBannerManager` class is responsible for providing a custom ASCII banner for the CLI application in which it's implemented.

## Overview

The `AsciiBannerManager` class is based on the concept of **figlet**, which is commonly described as "_a computer program that generates text banners, in a variety of typefaces, composed of letters made up of conglomerations of smaller ASCII characters_" (source: Wikipedia).

Implementing the whole figlet logic is out of the scope of this class. The class hardcodes an ASCII banner created by a third-party figlet and add some custom logic around it. 

The ASCII banner commonly returned by the `AsciiBannerManager` class can be generated using the following figlets and the "banner3-D" style:
 
- http://www.network-science.de/ascii/ 
- https://www.askapache.com/online-tools/figlet-ascii/

## The Minimum Width

To avoid that the banner triggers some horizontal scrolling when the CLI application displays it, it was important to have a minimum width to use as reference. 

Therefore I run the following command on the smallest devices in my collection, all running Linux: 

```sh
stty size
```

The command returned the following data:

| Device        | Output (stty) | Resolution | Terminal Font       |
|---------------|---------------|------------|---------------------|
| Hackberry Pi  | 33 x 70       | 720 x 720  | Monospace 12px      |
| Asus CM30     | 35 x 157      | 1200 x 750 | Noto Sans Mono 13px |
| Thinkpad x250 | 36 x 150      | 1200 x 800 | Monospace 12px      |

The reference minimum width I was looking for was **70 columns**. 

In the figlet world, to have your banner render within this minimum width when using "banner3-D", the name of the CLI application (used in the banner) must not have more than **six letters**. 

## Examples

Here some examples of ASCII banners provided by this class:

```
*****************************************************************
'##::: ##:'##:::::'##::'######:::::'###::::'##::::'##::'######:::
 ###:: ##: ##:'##: ##:'##... ##:::'## ##::: ##:::: ##:'##... ##::
 ####: ##: ##: ##: ##: ##:::..:::'##:. ##:: ##:::: ##: ##:::..:::
 ## ## ##: ##: ##: ##: ##:::::::'##:::. ##: ##:::: ##: ##::'####:
 ##. ####: ##: ##: ##: ##::::::: #########:. ##:: ##:: ##::: ##::
 ##:. ###: ##: ##: ##: ##::: ##: ##.... ##::. ## ##::: ##::: ##::
 ##::. ##:. ###. ###::. ######:: ##:::: ##:::. ###::::. ######:::
..::::..:::...::...::::......:::..:::::..:::::...::::::......::::
**********************************************Version: 2.0.0*****
```

```
*****************************************************
'##::: ##:'##:::::'##:'########::'######::'########::
 ###:: ##: ##:'##: ##:..... ##::'##... ##: ##.... ##:
 ####: ##: ##: ##: ##::::: ##::: ##:::..:: ##:::: ##:
 ## ## ##: ##: ##: ##:::: ##::::. ######:: ##:::: ##:
 ##. ####: ##: ##: ##::: ##::::::..... ##: ##:::: ##:
 ##:. ###: ##: ##: ##:: ##::::::'##::: ##: ##:::: ##:
 ##::. ##:. ###. ###:: ########:. ######:: ########::
..::::..:::...::...:::........:::......:::........:::
********************************Version: 2.0.0.0*****
```

```
******************************************************
'##::: ##:'##:::::'##:'########::'#######:::'#######::
 ###:: ##: ##:'##: ##:..... ##::'##.... ##:'##.... ##:
 ####: ##: ##: ##: ##::::: ##::: ##:::: ##: ##:::: ##:
 ## ## ##: ##: ##: ##:::: ##:::: ##:::: ##: ##:::: ##:
 ##. ####: ##: ##: ##::: ##::::: ##:::: ##: ##:::: ##:
 ##:. ###: ##: ##: ##:: ##:::::: ##:::: ##: ##:::: ##:
 ##::. ##:. ###. ###:: ########:. #######::. #######::
..::::..:::...::...:::........:::.......::::.......:::
***********************************Version: 3.0.0*****
```

```
*************************************************
'##::: ##:'##:::::'##:'########:::'######::'####:
 ###:: ##: ##:'##: ##: ##.... ##:'##... ##:. ##::
 ####: ##: ##: ##: ##: ##:::: ##: ##:::..::: ##::
 ## ## ##: ##: ##: ##: ########::. ######::: ##::
 ##. ####: ##: ##: ##: ##.... ##::..... ##:: ##::
 ##:. ###: ##: ##: ##: ##:::: ##:'##::: ##:: ##::
 ##::. ##:. ###. ###:: ########::. ######::'####:
..::::..:::...::...:::........::::......:::....::
******************************Version: 3.0.0*****
```

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)