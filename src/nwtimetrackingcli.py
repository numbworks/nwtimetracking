'''
    A CLI application that can run several automated data analysis tasks on a time tracking file and save the results as a PDF report. 
'''

# GLOBAL MODULES
import os
import subprocess
from argparse import _SubParsersAction, ArgumentParser, Namespace
from shutil import get_terminal_size
from subprocess import CompletedProcess
from typing import Any, Callable, Final, Optional

# LOCAL/NW MODULES
from nwtimetracking import OPTION, TimeTrackingProcessor, ComponentBag, SettingBag, YearProvider
from setupinfo import PROJECT_VERSION, CLI_DESCRIPTION

# CONSTANTS
class CLISTRING:

    '''Collects all the CLI-related strings.'''

    COMMAND_DEST : Final[str] = "command"
    COMMAND_REQUIRED : Final[bool] = True
    COMMAND_ARGS : dict[str, Any] = { "dest": COMMAND_DEST, "required": COMMAND_REQUIRED }

    COMMAND_SAVE_NAME : Final[str] = "save"
    COMMAND_SAVE_HELP : Final[str] = "Runs all the data analysis tasks against the time tracking file and saves the outcome as PDF report."

    OPTION_INPUTPATH_FLAGS : Final[list[str]] = ["--input_path"]
    OPTION_INPUTPATH_DEST : Final[str] = "input_path"
    OPTION_INPUTPATH_REQUIRED : Final[bool] = True
    OPTION_INPUTPATH_HELP : Final[str] = "The path to the time tracking file in Excel format."

    OPTION_NROWS_FLAGS : Final[list[str]] = ["--nrows"]
    OPTION_NROWS_DEST : Final[str] = "nrows"
    OPTION_NROWS_REQUIRED : Final[bool] = True
    OPTION_NROWS_HELP : Final[str] = "Latest row number to process in the time tracking file."

    OPTION_FOLDERPATH_FLAGS : Final[list[str]] = ["--folder_path"]
    OPTION_FOLDERPATH_DEST : Final[str] = "folder_path"
    OPTION_FOLDERPATH_REQUIRED : Final[bool] = False
    OPTION_FOLDERPATH_HELP : Final[str] = "The path to the folder into which the PDF report will be saved. Default: current folder."

# STATIC CLASSES
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

# CLASSES
class AsciiBannerManager:

    """
        Creates the ASCII banner for the provided library's version.

        The figlet can be generated using 
            - 'http://www.network-science.de/ascii/' (font: "banner3-D", width: 120)
            - 'https://www.askapache.com/online-tools/figlet-ascii/'.
    """

    def __validate(self, version: str) -> None:
        
        """Validates the provided 'version'."""

        if not version or not version.strip():
            raise ValueError(_MessageCollection.provided_version_empty_whitespace())
    def __create_figlet(self) -> tuple:
        
        """Returns a tuple containing the figlet and its width."""
        
        lines : list[str] = [
            "'##::: ##:'##:::::'##:'########:'####:'##::::'##:'########:",
            " ###:: ##: ##:'##: ##:... ##..::. ##:: ###::'###: ##.....::",
            " ####: ##: ##: ##: ##:::: ##::::: ##:: ####'####: ##:::::::",
            " ## ## ##: ##: ##: ##:::: ##::::: ##:: ## ### ##: ######:::",
            " ##. ####: ##: ##: ##:::: ##::::: ##:: ##. #: ##: ##...::::",
            " ##:. ###: ##: ##: ##:::: ##::::: ##:: ##:.:: ##: ##:::::::",
            " ##::. ##:. ###. ###::::: ##::::'####: ##:::: ##: ########:",
            "..::::..:::...::...::::::..:::::....::..:::::..::........::"
        ]

        return (os.linesep.join(lines), len(lines[0]))
    def __create_frame(self, version: str, max_length: int) -> tuple:
        
        """Returns a tuple containing the frame of the figlet."""
        
        version_token : str = f"Version: {version}"
        
        margin_length : int = 5
        total_length : int = max_length - len(version_token) - margin_length

        top_line : str = "*" * max_length
        bottom_line : str = f"{top_line[:total_length]}{version_token}{'*' * margin_length}"

        return (top_line, bottom_line)

    def create_standard(self, version : str) -> str:
        
        """Creates the standard ASCII banner."""
        
        self.__validate(version)

        figlet, max_length = self.__create_figlet()
        top_line, bottom_line = self.__create_frame(version, max_length)

        ascii_banner : str = os.linesep.join([
            top_line,
            figlet,
            bottom_line,
            ""
        ])

        return ascii_banner
    def create_mini(self, version : str) -> str:

        """
            Creates the mini ASCII banner:
            
                *****************
                * NWTIME v1.0.0 *
                *****************
        """

        self.__validate(version)

        assembly_name : str = "NWTIME"
        middle_line : str = f"* {assembly_name} v{version} *"
        
        top_line : str = "*" * len(middle_line)
        bottom_line : str = top_line

        ascii_banner : str = os.linesep.join([
            top_line,
            middle_line,
            bottom_line,
            ""
        ])

        return ascii_banner
    def create(self, version : str, terminal_width : int) -> str:

        """Creates either a standard or mini ASCII banner depending on the terminal width."""
        
        _, max_length = self.__create_figlet()

        if max_length <= terminal_width:
            return self.create_standard(version)
        else:
            return self.create_mini(version)
class TerminalWindowManager:

    '''Handles terminal window size.'''

    __shutil_width_function : Callable[[], Optional[int]]
    __stty_width_function : Callable[[], Optional[int]]

    cutoff_width : Final[int] = 70

    @staticmethod
    def default_shutil_width_function() -> Optional[int]:

        """Get terminal width using shutil (multi-platform)."""

        try:

            terminal_width : int = get_terminal_size().columns

            return terminal_width
        
        except:
            return None

    @staticmethod
    def default_stty_width_function() -> Optional[int]:

        """Get terminal width using stty command (Linux)."""

        try:

            process : CompletedProcess[str] = subprocess.run(
                ["/bin/sh", "-c", "stty size | cut -d' ' -f2"],
                capture_output = True,
                text = True,
                check = False,
            )

            stty_output : str = process.stdout.strip()
            terminal_width : int = int(stty_output)

            if terminal_width >= 0:
                return terminal_width

            return None
        except:
            return None

    def __init__(
        self,
        shutil_width_function : Optional[Callable[[], Optional[int]]] = None,
        stty_width_function : Optional[Callable[[], Optional[int]]] = None,
    ) -> None:
        
        if shutil_width_function is None:
            shutil_width_function = self.default_shutil_width_function
        
        if stty_width_function is None:
            stty_width_function = self.default_stty_width_function

        self.__shutil_width_function = shutil_width_function
        self.__stty_width_function = stty_width_function

    def get_or_cutoff(self) -> int:

        terminal_width : Optional[int] = self.__shutil_width_function()

        if terminal_width is None:
            terminal_width = self.__stty_width_function()

        if terminal_width is None:
            terminal_width = self.cutoff_width

        return terminal_width
class Validator:

    '''Collects all validation methods.'''

    @staticmethod
    def validate_file_path(file_path : str) -> None:

        """Raises an exception if file_path doesn't exist."""
        
        if not os.path.isfile(file_path):
            raise Exception(_MessageCollection.provided_path_doesnt_exist(file_path))
    
    @staticmethod
    def validate_folder_path(folder_path : str) -> None:

        """Raises an exception if folder_path doesn't exist."""
        
        if not os.path.isdir(folder_path):
            raise Exception(_MessageCollection.provided_path_doesnt_exist(folder_path))

    @staticmethod
    def validate_nrows(nrows : str) -> None:

        """Raises an exception if nrows is not a valid integer or if it's < 1."""
        
        try:
            int(nrows)
        except ValueError:
            raise Exception(_MessageCollection.provided_nrows_not_valid_integer(nrows))
        
        if int(nrows) < 1:
            raise Exception(_MessageCollection.provided_nrows_less_one(nrows))
class CLIValidator:

    '''Handles CLI argument validation.'''

    def validate_file_path(self, file_path: str) -> str:

        '''Returns file_path or raises Exception.'''

        Validator().validate_file_path(file_path)

        return file_path
    def validate_folder_path(self, folder_path: str) -> str:

        '''Returns folder_path or raises Exception.'''

        Validator().validate_folder_path(folder_path)

        return folder_path
    def validate_nrows(self, nrows : str) -> str:

        '''Returns nrows or raises Exception.'''

        Validator().validate_nrows(nrows)

        return nrows
class APFactory():

    '''Encapsulates all the logic related to the creation of a custom instance of argparse.ArgumentParser.'''

    __cli_validator : CLIValidator

    def __init__(self, cli_validator : CLIValidator = CLIValidator()) -> None:
        self.__cli_validator = cli_validator

    def __add_option_input_path(self, argument_parser : ArgumentParser) -> None:
        
        '''Adds the option mentioned in the method name.'''
        
        argument_parser.add_argument(
            *CLISTRING.OPTION_INPUTPATH_FLAGS,
            dest = CLISTRING.OPTION_INPUTPATH_DEST,
            required = CLISTRING.OPTION_INPUTPATH_REQUIRED,
            help = CLISTRING.OPTION_INPUTPATH_HELP,
            type = self.__cli_validator.validate_file_path
        )
    def __add_option_nrows(self, argument_parser : ArgumentParser) -> None:
        
        '''Adds the option mentioned in the method name.'''
        
        argument_parser.add_argument(
            *CLISTRING.OPTION_NROWS_FLAGS,
            dest = CLISTRING.OPTION_NROWS_DEST,
            required = CLISTRING.OPTION_NROWS_REQUIRED,
            help = CLISTRING.OPTION_NROWS_HELP,
            type = self.__cli_validator.validate_nrows
        )
    def __add_option_folder_path(self, argument_parser : ArgumentParser) -> None:
        
        '''Adds the option mentioned in the method name.'''
        
        argument_parser.add_argument(
            *CLISTRING.OPTION_FOLDERPATH_FLAGS,
            dest = CLISTRING.OPTION_FOLDERPATH_DEST,
            required = CLISTRING.OPTION_FOLDERPATH_REQUIRED,
            help = CLISTRING.OPTION_FOLDERPATH_HELP,
            type = self.__cli_validator.validate_folder_path
        )

    def create(self) -> ArgumentParser:

        '''
            Creates a custom instance of argparse.ArgumentParser.

            The "prog" argument is not provided in order to make the "usage" statement dynamic:

                usage: nwtimetrackingcli.py [-h] ...
        '''

        argument_parser : ArgumentParser = ArgumentParser(description = CLI_DESCRIPTION)
        root : _SubParsersAction[ArgumentParser] = argument_parser.add_subparsers(**CLISTRING.COMMAND_ARGS)

        saveparser : ArgumentParser = root.add_parser(
            name = CLISTRING.COMMAND_SAVE_NAME, 
            help = CLISTRING.COMMAND_SAVE_HELP
        )

        self.__add_option_input_path(saveparser)
        self.__add_option_nrows(saveparser)
        self.__add_option_folder_path(saveparser)

        return argument_parser
class TimeTrackingProcessorFactory:

    '''Factory for TimeTrackingProcessor.'''

    def create(self, component_bag : ComponentBag, setting_bag : SettingBag) -> TimeTrackingProcessor:

        '''Creates instances of TimeTrackingProcessor'''

        return TimeTrackingProcessor(component_bag, setting_bag)
class CLIManager():

    '''Collects all the logic related to the CLI management.'''

    __ap_factory : APFactory
    __ascii_banner_manager : AsciiBannerManager
    __rl_factory : TimeTrackingProcessorFactory
    __tw_manager : TerminalWindowManager
    __logging_function : Callable[[str], None]

    def __init__(
        self, 
        ap_factory : APFactory = APFactory(), 
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager(),
        rl_factory : TimeTrackingProcessorFactory = TimeTrackingProcessorFactory(),
        tw_manager : TerminalWindowManager = TerminalWindowManager(),
        logging_function : Callable[[str], None] = lambda msg : print(msg)) -> None:
        
        self.__ap_factory = ap_factory
        self.__ascii_banner_manager = ascii_banner_manager
        self.__rl_factory = rl_factory
        self.__tw_manager = tw_manager
        self.__logging_function = logging_function

    def __log_ascii_banner(self) -> None:

        '''Logs the ASCII banner.'''

        terminal_width : int = self.__tw_manager.get_or_cutoff()
        ascii_banner : str = self.__ascii_banner_manager.create(PROJECT_VERSION, terminal_width)

        self.__logging_function("")
        self.__logging_function(ascii_banner)
    def __log_namespace(self, namespace : Namespace):

        '''Logs the provided args.'''

        for key, value in vars(namespace).items():
            self.__logging_function(f"{key}: '{value}'")
            
        self.__logging_function("")
    
    def __get_cwd_path(self) -> str:

        '''Get current folder.'''

        cwd_path : str = os.getcwd()

        return cwd_path
    def __create_setting_bag(self, input_path : str, nrows : str, folder_path : str) -> SettingBag:

        """Creates a SettingBag object."""

        setting_bag : SettingBag = SettingBag(
            options_tt = [OPTION.display],
            options_tt_latest_four = [OPTION.display],
            options_tts_by_month = [OPTION.display],
            options_tts_by_year = [OPTION.display],
            options_tts_by_range = [OPTION.display],
            options_tts_by_spn = [OPTION.display],
            options_tts_by_spv = [OPTION.display],
            options_tts_by_hashtag_year = [OPTION.display],
            options_tts_by_hashtag = [OPTION.display],
            options_tts_by_year_month_spnv = [OPTION.display],
            options_tts_by_timeranges = [OPTION.display],
            options_ttd_effort_status = [OPTION.display],
            options_definitions = [OPTION.display],
            options_report = [OPTION.save_pdf],
            excel_path = input_path,
            excel_nrows = int(nrows),
            working_folder_path = folder_path,
            tts_by_spv_software_project_names = ["nwrefurbishedanalytics", "NW.ZooSketchDownloader", "nwcommitaverages"]
        )

        return setting_bag
    def __run_when_save(self, namespace : Namespace) -> None:
        
        '''Dispatches the provided arguments to the corresponding actions.'''

        component_bag : ComponentBag = ComponentBag()

        setting_bag : SettingBag = self.__create_setting_bag(
            input_path = namespace.input_path,
            nrows = namespace.nrows,
            folder_path = namespace.folder_path
        )

        rl_processor : TimeTrackingProcessor = self.__rl_factory.create(component_bag, setting_bag)
        rl_processor.initialize()
        rl_processor.save_as_report()

        self.__logging_function(_MessageCollection.pdf_report_successfully_saved())
    def __dispatch(self, namespace : Namespace) -> None:
        
        '''Dispatches the provided arguments to the corresponding actions.'''

        if not namespace.folder_path:
            namespace.folder_path = self.__get_cwd_path()

        if namespace.command == CLISTRING.COMMAND_SAVE_NAME:
            self.__run_when_save(namespace)

    def run_and_log(self) -> None:

        '''
            Performs the user-provided and log them.
            
            The SystemExit exception occurs when a required option is not provided.
            SystemExit doesn't inherit from Exception and has no message, therefore we need to handle it accordingly.            
        '''

        try:

            self.__log_ascii_banner()

            argument_parser : ArgumentParser = self.__ap_factory.create()
            namespace : Namespace = argument_parser.parse_args()

            self.__log_namespace(namespace)          
            self.__dispatch(namespace)

        except (Exception, SystemExit) as e:
            
            if not isinstance(e, SystemExit):
                self.__logging_function(str(e))

# MAIN
def main(): CLIManager().run_and_log()

if __name__ == "__main__":
    main()