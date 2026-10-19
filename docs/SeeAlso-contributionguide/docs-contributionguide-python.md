# contribuitionguide-python
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2023-05-20 | numbworks | Created. |
| 2027-07-26 | numbworks | Last update. |

## Overview

This document collects all the guidelines to follow for anyone who would like to contribute code to this project.

## Disclaimer

External contributions are welcome, though they must align with the intended purpose and roadmap of this project, and comply with all guidelines outlined in this document.

## Principles and Best Practices

Python is a multi-paradigm programming language (object-oriented, procedural and functional). This project adopts the object‑oriented approach.

Below a list of principles and best practice that are widely adopted in the codebase:

1. **Maintainability First**. The highest cost in the software industry is the maintanance of a software over time, not its creation.
2. **Software Usability** as part of the **Definition-of-Done**. Usable software is pleasurable for the users to use and for the developers to maintain.
3. **Documentation** as part of the **Definition-of-Done**. Every release should include up-to-date documentation. Actual documentation makes the software faster to learn for the users and easier to debug for the developers. 
4. **DRY Principle**. Write a certain piece of code once, reference it millions of times.
5. **Single Responsability Principle** (SOLID). Every class should have one single responsability, even when you might end up having many very small classes.
6. **Interface Segregation Principle** (SOLID). Better to have a lot of smaller interfaces than a few bigger ones.
7. **Dependency Inversion Principle** (SOLID). Your code should always depend upon abstractions, not upon concrete classes.
8. **Composition over inheritance**. Objects form an opportunistic "has a" relationship with other objects that contain the logic they need, rather than a parent–child relationship that can become difficult to maintain as the codebase grows. In some occasions, inheritance can be used with **abstract classes**.
9. **Design Patterns**. You'll find a heavy use of **Factory Pattern**, **Repository Pattern** and **Object Mother Pattern** (for unit testing).
10. **Strong focus on unit testing**. Software must maintain unit test coverage above 70% and adhere to established testing best practices, including consistent test‑naming conventions (e.g., BDD style), and appropriate use of mocks and fakes.
11. **Naming convention**. Classes, variables and projects must be named consistently according to a defined domain‑specific language and established naming conventions known to improve code readability, such as hierarchical naming.
12. **Templating**. Custom class and method templates should be used consistently across the codebase to standardize structure, enforce uniform patterns and maximize development speed.
13. **Minimal set of external dependencies**. External software packages must be introduced only when they provide clear, measurable value, as each dependency adds long‑term maintenance overhead and requires ongoing lifecycle management.
14. **Minimal set of arguments**. Methods should accept the minimum number of arguments necessary. When appropriate, related arguments should be grouped into dedicated parameter classes to improve method readability and maintainability.

## Clean Architecture

**Clean Architecture** is a software design approach that structures an application into independent, concentric layers, ensuring that business logic stays isolated from frameworks, databases, and UI. The key idea is that all dependencies must point inward, toward the core business rules.

For example, when developing a CLI application, we encapsulate all business logic in a library project and place the delivery mechanism (the CLI) in a separate project:

```
- /src/
	- nwtimetracking.py
	- nwtimetrackingcli.py
```

The inner circle corresponds to the library, while the outer circle corresponds to the CLI. In other words, the CLI depends on the library, but the library remains independent of the CLI.

This separation of concerns is also present in other two well‑known architectural styles:

- **Hexagonal Architecture** -  the CLI is an adapter and the library is the domain. The CLI simply forwards requests to the domain layer.
- **Layered Architecture** - the CLI represents the application layer, while the library represents the domain layer.

## The Primary Constructor

Public and private properties of a class should be assigned exclusively through the constructor. This approach ensures:

1. **Centralized validation**, in line with the DRY principle.
2. **Elimination of hidden side effects** caused by scattered validation logic.
3. **Consistent object creation**, improving long‑term maintainability.
4. **Immutability benefits**, including thread safety, reference caching, and other performance and security advantages.

```python
class TTDataFrameFactory():

    __df_helper : TTDataFrameHelper

    def __init__(self, df_helper : TTDataFrameHelper) -> None:

        self.__df_helper = df_helper
    ...
```

```python
@dataclass(frozen=True)
class SettingBag():

    '''Represents a collection of settings.'''

    # WITHOUT DEFAULTS
    options_tt : list[Literal[OPTION.display]]
    options_tt_latest_four : list[Literal[OPTION.display]]
    options_tts_by_month : list[Literal[OPTION.display]]

    # WITH DEFAULTS
    options_ttd_effort_status : list[Literal[OPTION.display]] = field(default_factory = list)
    working_folder_path : str = field(default = "/home/nwtimetracking/")
    excel_path : str = field(default = DefaultPathProvider().get_default_time_tracking_path())
    excel_skiprows : int = field(default = 0)
```

There may be exceptions when working with **DTOs** (**Data Transfer Objects**) that do not require validation and are intended for internal or private use. In these cases, non‑immutable public properties can be acceptable when immutability would add unnecessary complexity or reduce clarity.

## The Entry-Point Class

Each module has a public **entry-point class**, which conveniently collects and exposes all the available methods to the consumer. The **entry-point class** summarizes how the consumer is allowed to interact with the module or, in other words, it exposes all the use cases that have been considered for the module so far.

To simplify its initialization, the **entry-point class** doesn't exist without two other classes:

- A `SettingBag` class, collecting all the settings that the module requires the user to provide in order to run.
- A `ComponentBag` class, collecting all the dependencies that the module requires in order to run.

The concept behind these two classes can be defined as **The Bag Pattern**, and both classes are provided to the **entry-point class** thru its constructor:

```python
...
class TimeTrackingProcessor():

    def __init__(self, component_bag : ComponentBag, setting_bag : SettingBag) -> None:

        self.__component_bag = component_bag
        self.__setting_bag = setting_bag
    ...
```

## Internal And External Business Logic

Each class has two kinds of business logic: 

- **Internal logic**, when the class provides the behavior itself.
- **External logic**, when the behavior is delegated to another class.

Additionally, according to the **Single Responsibility Principle**, every class should have one clear responsibility. Non‑specific or cross‑cutting logic should be moved into its own dedicated class. For example, all serialization‑related logic should be collected in a `Serializer` class (or placed under a `Serialization` namespace).

The entry‑point class is a good example of this pattern: most of its behavior comes from its dependencies, and the entry‑point class acts primarily as a “junction” between those dependencies and the library user.

```python
class TimeTrackingProcessor():

	__component_bag : ComponentBag
	
	... 
	
	def initialize(self) -> None:

		self.__tt_summary = self.__component_bag.tt_adapter.create_summary(
			setting_bag = self.__setting_bag)
	...
```

## Private Methods

The use of `private` methods is absolutely incentivized, because: 

- They massively help to break the code in smaller parts within the same class, minimizing duplication and maximizing re-use
- They maximize the readibility of the `public` methods

```python
class TTReportManager():

	...
	def __create_report_file_paths(self, ...) -> Tuple[Path, Path]: ...
	def __create_html_sections(self, ...) -> list[str]: ...
	def __create_html_template(self, ...) -> str: ...
	
	...
	def save_as_report(self, ...) -> None:
	
		...
		html_path, pdf_path = self.__create_report_file_paths(
			folder_path = folder_path, 
			last_update = last_update)
        
		html_sections : list[str] = self.__create_html_sections(
			tt_summary = tt_summary, 
			formatters = formatters)
        
		full_html : str = self.__create_html_template(
			html_sections = html_sections, 
			last_update = last_update)
		...
	...
```

## The Session Object

It's good practice to define a `Session` object, to collect all the possible outcome objects generated by the library's entry-point class. 

This practice allows to post-pone the decision about what to use to a later stage.

```python
...
@dataclass(frozen = True)
class TTSummary():

    '''Collects all the dataframes, stylers and markdowns.'''

    tt_df : DataFrame
    tt_latest_four_df : DataFrame
    tts_by_month_df : DataFrame
    tts_by_year_df : DataFrame
    tts_by_range_df : DataFrame
    tts_by_spn_df : DataFrame
    tts_by_spv_df : DataFrame
    tts_by_hashtag_year_df : DataFrame
    tts_by_hashtag_df : DataFrame
    tts_by_year_month_spnv_df : DataFrame
    tts_by_timeranges_df : DataFrame
    ttd_effort_status_df : DataFrame
    definitions_df : DataFrame
```

```python
class TimeTrackingProcessor():

	...
	def get_summary(self) -> TTSummary:

		... 
		self.__validate_summary()

		return self.__tt_summary
...
```

Having a dedicated session object aligns well with **Clean Architecture** principles because:

- It keeps the domain results cohesive (**session encapsulation**).
- It allow the delivery mechanism (CLI, API, GUI) to decide what to display or persist (**deferred decisions**).
- It ensures that the library's entry-point class doesn't return presentation-specific constructs.

## The ComponentBag Object

The `ComponentBag` object collects all the dependencies into a single place, including any default logic, and is passed to the library’s entry-point class. This object has the responsibility of providing all the necessary dependencies to the entry-point.

```python
@dataclass(frozen=True)
class ComponentBag():

    '''Represents a collection of components.'''

    file_path_manager : FilePathManager = field(default = FilePathManager())
    file_manager : FileManager = field(default = FileManager(file_path_manager = FilePathManager()))
    displayer : Displayer = field(default = Displayer())
    ttr_manager : TTReportManager = field(default = TTReportManager())
    tt_adapter : TTAdapter = field(default = TTAdapter(
        df_factory = TTDataFrameFactory(df_helper = TTDataFrameHelper()),
        effort_highlighter = EffortHighlighter(df_helper = TTDataFrameHelper())))
```

```python
class TimeTrackingProcessor():

    '''Collects all the logic related to the processing of "Time Tracking.xlsx".'''

    __component_bag : ComponentBag
    __setting_bag : SettingBag
    __tt_summary : TTSummary

    def __init__(self, component_bag : ComponentBag, setting_bag : SettingBag) -> None:

        self.__component_bag = component_bag
        self.__setting_bag = setting_bag
	...
```

On **Clean Architecture**'s terms, the `ComponentBag` object acts as a **composition root for the domain**. 

The **composition root for the domain** is the place where all domain dependencies are assembled and configured before being passed into the domain’s entry point. It is the single, centralized location responsible for constructing the domain with the exact set of collaborators it needs, while keeping the domain itself free of creation logic.

## The SettingBag Object

The `SettingBag` object collects all the relevant settings, including their eventual default values, into a single place, and is passed to the library’s entry-point class. This object has the responsibility of providing all the settings that the user may want to customize to the entry-point.

```python
@dataclass(frozen=True)
class SettingBag():

    '''Represents a collection of settings.'''

    # WITHOUT DEFAULTS
    options_tt : list[Literal[OPTION.display]]
    options_tt_latest_four : list[Literal[OPTION.display]]
    options_tts_by_month : list[Literal[OPTION.display]]

    # WITH DEFAULTS
    options_ttd_effort_status : list[Literal[OPTION.display]] = field(default_factory = list)
    working_folder_path : str = field(default = "/home/nwtimetracking/")
    excel_path : str = field(default = DefaultPathProvider().get_default_time_tracking_path())
    excel_skiprows : int = field(default = 0)
```

```python
class TimeTrackingProcessor():

    '''Collects all the logic related to the processing of "Time Tracking.xlsx".'''

    __component_bag : ComponentBag
    __setting_bag : SettingBag
    __tt_summary : TTSummary

    def __init__(self, component_bag : ComponentBag, setting_bag : SettingBag) -> None:

        self.__component_bag = component_bag
        self.__setting_bag = setting_bag
	...
```

On **Clean Architecture**'s terms, the `SettingBag` object acts as a **configuration provider  for the domain**. 

The **configuration provider for the domain** is a component that supplies the domain with all runtime settings and customizable parameters it needs, without embedding configuration logic inside the domain itself. It centralizes defaults and user‑defined values so the domain can operate with stable, validated settings.

## The MessageCollection Class

The `MessageCollection` class is static and centralizes all messages in a single place, including both logging messages and exception messages. This centralization helps developers to use a cohesive and consistent language throughout the entire application.

```python
...
class _MessageCollectionAsciiBannerManager:

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def provided_version_empty_whitespace() -> str:
        return "The provided 'version' is empty or whitespace."
class _MessageCollectionValidator:

    '''Collects all the messages used for logging and for the exceptions used by Validator.'''

    @staticmethod
    def provided_path_doesnt_exist(path : str) -> str:
        return f"The provided path doesn't exist: '{path}'."

    @staticmethod
    def provided_nrows_not_valid_integer(nrows : str) -> str:
        return f"The provided 'nrows' is not a valid integer: '{nrows}'."

    @staticmethod
    def provided_nrows_less_one(nrows : str) -> str:
        return f"The provided 'nrows' can't be less than one: '{nrows}'."
class _MessageCollectionCLIManager:

    '''Collects all the messages used for logging and for the exceptions used by CLIManager.'''

    @staticmethod
    def pdf_report_successfully_saved() -> str:
        return "The PDF report has been successfully saved."
class _MessageCollection(
        _MessageCollectionAsciiBannerManager,
        _MessageCollectionValidator,
        _MessageCollectionCLIManager):

    '''Collects all the messages used for logging and for the exceptions.'''
...
```

It's a more future-proof practice to have one `MessageCollection` class for each class.

## Inline Documentation

Inline documentation (**Docstrings**) is mandatory for public members, such as classes, interfaces and methods. It's optional for public properties and private members.

```python
class FilePathManager():
    
    '''Collects all the logic related to the file path management.'''

    def create_file_path(self, folder_path : str, file_name : str) -> str:

        '''Creates a file path.'''

        return os.path.join(folder_path, file_name) 
    def create_numbered_file_path(self, folder_path : str, number : int, extension : str) -> str:

        r'''Creates a numbered file path. Example: ("C:\\", 1, "html") => "C:\\1.html"'''

        file_name : str = f"{number}.{extension}"
        file_path : str = self.create_file_path(folder_path = folder_path, file_name = file_name)    

        return file_path
```

Some additional guidelines:

- When possible, it's good practice to use one-line docstrings.
- When the method manipulates data, it's good practice to document the first and after in the docstring.

## Unit Test Structure

The unit tests are grouped per module:

```
- /src/
	- nwtimetracking.py
	- nwtimetrackingcli.py
- /tests/
	- nwtimetrackingtests.py
	- nwtimetrackingclitests.py
```

## Unit Test Framework

We adopt `unittest` as the testing framework, augmented with `parameterized` for the parametric tests:

```python
from unittest import TestCase
from parameterized import parameterized
...
```

## Unit Test Naming Convention

The unit tests:

- Can be standard or parametric (when required).
- Must follow the **Arrange-Act-Assert (AAA)** pattern.
- Must use test names that follow the **Behavior-Driven Development (BDD)** naming convention (Should...When).
- Must adopt the **Object Mother** pattern when the same object is required by multiple test classes.

```python
...
class TimeTrackingProcessorTestCase(unittest.TestCase):

    def test_processtt_shoulddisplay_whenoptionisdisplay(self) -> None:
        
        # Arrange
        tt_df : DataFrame = Mock()

        summary : Mock = Mock()
        summary.tt_df = tt_df

        displayer : Mock = Mock()
        tt_adapter : Mock = Mock()
        tt_adapter.create_summary.return_value = summary

        component_bag : Mock = Mock()
        component_bag.displayer = displayer
        component_bag.tt_adapter = tt_adapter

        setting_bag : Mock = Mock()
        setting_bag.options_tt = [OPTION.display]   # type: ignore

        # Act
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = component_bag, setting_bag = setting_bag)
        tt_processor.initialize()
        tt_processor.process_tt()

        # Assert
        displayer.display.assert_called_once_with(obj = tt_df)

    ...

    @parameterized.expand([
        ["process_tt"],
        ["process_tt_latest_four"],
        ["process_tts_by_month"]
    ])
    def test_processmethod_shouldraiseexception_wheninitializenotrun(self, method_name : str) -> None:
        
        # Arrange
        tt_processor : TimeTrackingProcessor = TimeTrackingProcessor(component_bag = Mock(), setting_bag = Mock())

        # Act & Assert
        with self.assertRaises(Exception) as context:
            getattr(tt_processor, method_name)()

        self.assertEqual(str(context.exception), "Please run the 'initialize' method first.")
```

## Unit Test Coverage

We aim for <u>at least 70% code coverage</u> for each module.

## Source

Most of the code used in the example blocks comes from the following project:

- [nwtimetracking](https://github.com/numbworks/nwtimetracking)

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)
