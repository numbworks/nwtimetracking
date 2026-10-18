'''A script to build and publish on TestPyPi/PyPi.'''

# GLOBAL MODULES
import argparse
import importlib.util
import shutil
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess

# STATIC CLASSES
class MessageCollection:

    """Collects all the messages used for logging and for the exceptions."""

    @staticmethod
    def required_modules(required : list[str]) -> str:
        required_str : str = ", ".join(required)
        return f"[OK] Required Python modules have been found: [{required_str}]."

    @staticmethod
    def missing_modules(missing : list[str]) -> str:
        missing_str : str = ", ".join(missing)
        return f"[ERROR] Required Python module(s) missing: [{missing_str}]. Please install them via 'pip install {missing_str}' and try again."

    @staticmethod
    def cleaned_directory(path : Path) -> str:
        return f"[OK] Cleaned existing directory: {path}"

    @staticmethod
    def created_directory(path : Path) -> str:
        return f"[OK] Created directory: {path}"

    @staticmethod
    def copied_file(src : Path, dest : Path) -> str:
        return f"[OK] Copied '{src}' -> '{dest}'"

    @staticmethod
    def file_is_missing(path : Path) -> str:
        return f"[ERROR] File is missing: {path}"

    @staticmethod
    def closing_parenthesis_not_found() -> str:
        return "[ERROR] Could not locate closing setup() parenthesis in setup.py."

    @staticmethod
    def build_successful() -> str:
        return "[OK] Package build has been successful."

    @staticmethod
    def build_failed() -> str:
        return "[ERROR] Package build failed."
    
    @staticmethod
    def no_dist_files_found() -> str:
        return "[ERROR] No distribution files found in dist directory."

    @staticmethod
    def twine_validation_failed() -> str:
        return "[ERROR] Twine validation failed! Expected all checks to pass."
    
    @staticmethod
    def twine_validation_successful() -> str:
        return "[OK] Twine validation successful!"

    @staticmethod
    def following_exception_raised(e : Exception, dir_staging : Path) -> str:
        return (
            f"[ERROR] The following exception has been raised: '{str(e).replace("[ERROR] ", "")}'."
            "\n"
            f"[INFO] Staging directory preserved for debugging reasons: '{dir_staging}'")

    @staticmethod
    def twine_upload_testpypi_successful() -> str:
        return "[OK] Package successfully uploaded to TestPyPI!"

    @staticmethod
    def twine_upload_testpypi_failed() -> str:
        return "[ERROR] Twine upload to TestPyPI failed."

    @staticmethod
    def twine_upload_pypi_successful() -> str:
        return "[OK] Package successfully uploaded to PyPI!"

    @staticmethod
    def twine_upload_pypi_failed() -> str:
        return "[ERROR] Twine upload to PyPI failed."

    @staticmethod
    def testpypi_url(project_name : str) -> str:
        return f"[OK] TestPyPi URL: 'https://test.pypi.org/project/{project_name}/'."

    @staticmethod
    def pypi_url(project_name : str) -> str:
        return f"[OK] PyPi URL: 'https://pypi.org/project/{project_name}/'."

    @staticmethod
    def publishing_process_completed() -> str:
        return "[OK] Publishing process completed."

# CLASSES
@dataclass(frozen=True)
class SettingCollection:

    """Immutable collection of all build configuration settings."""

    project_name: str
    dir_repository: Path
    dir_publisher: Path
    dir_staging: Path
    dir_dist: Path
    dir_src: Path

    source_files : list[tuple[Path, Path]]
    readme_file : tuple[Path, Path]
    setup_file_staging : Path

    testpypi_username: str
    testpypi_password: str

    pypi_username: str
    pypi_password: str
class SettingCollectionFactory:
    
    """Factory for constructing SettingCollection objects."""

    def __create_source_files(self, dir_src : Path, dir_staging : Path) -> list[tuple[Path, Path]]:

        """Returns a list of (source_path, destination_path) tuples for all .py files in dir_src."""
        
        source_files : list[tuple[Path, Path]] = []

        for source_path in dir_src.glob("*.py"):
            destination_path : Path = dir_staging.joinpath(source_path.name)
            source_files.append((source_path, destination_path))

        return source_files
    def __create_readme_file(self, dir_publisher : Path, dir_staging : Path) -> tuple[Path, Path]:

        '''Returns (source_path, destination_path) for the README.md file.'''

        file_name : str = "README.md"

        source_path : Path = dir_publisher / file_name
        destination_path : Path = dir_staging / file_name

        return (source_path, destination_path)
    def __load_api_key(self, dir_publisher : Path, api_key_file_name : str) -> str:

        """Reads the API key from a text file in the publisher directory."""
        
        api_key_file_path: Path = dir_publisher.joinpath(api_key_file_name)

        if not api_key_file_path.exists():
            raise FileNotFoundError(MessageCollection.file_is_missing(api_key_file_path))
        
        api_key : str = api_key_file_path.read_text(encoding = "utf-8").strip()

        return api_key

    def create(self, project_name : str) -> SettingCollection:

        """Creates the default SettingCollection object."""

        dir_repository : Path = Path("/workspaces").joinpath(project_name)
        dir_staging : Path = Path("/tmp").joinpath(project_name)
        dir_publisher : Path = dir_repository.joinpath("scripts", "nwpublishers")
        dir_dist : Path = Path("/tmp/dist")
        dir_src : Path = dir_repository.joinpath("src")

        source_files : list[tuple[Path, Path]] = self.__create_source_files(dir_src = dir_src, dir_staging = dir_staging)
        readme_file : tuple[Path, Path] = self.__create_readme_file(dir_publisher = dir_publisher, dir_staging = dir_staging)
        setup_file_staging : Path = dir_staging.joinpath("setup.py")

        testpypi_username : str = "__token__"
        testpypi_password : str = self.__load_api_key(dir_publisher = dir_publisher, api_key_file_name = "TESTPYPI_API_KEY.txt")

        pypi_username : str = "__token__"
        pypi_password : str = self.__load_api_key(dir_publisher = dir_publisher, api_key_file_name = "PYPI_API_KEY.txt")

        return SettingCollection(
            project_name = project_name,
            dir_repository = dir_repository,
            dir_publisher = dir_publisher,
            dir_staging = dir_staging,
            dir_dist = dir_dist,
            dir_src = dir_src,
            source_files = source_files,
            readme_file = readme_file,
            setup_file_staging = setup_file_staging,
            testpypi_username = testpypi_username,
            testpypi_password = testpypi_password,
            pypi_username = pypi_username,
            pypi_password = pypi_password,
        )

# METHODS
def check_dependencies() -> None:

    """Ensure required dependencies are installed in the current environment."""
    
    required : list[str] = ["build", "twine"]
    missing : list[str] = []

    for package in required:
        if importlib.util.find_spec(package) is None:
            missing.append(package)

    if missing:
        print(MessageCollection.missing_modules(missing), file=sys.stderr)
        sys.exit(1)

    print(MessageCollection.required_modules(required))
def parse_arguments() -> tuple[bool, bool]:

    """Parses command line arguments."""

    parser : ArgumentParser = ArgumentParser(description = "Build and publish Python packages.")
    parser.add_argument("--enable_testpypi", action = "store_true", help = "Enable publishing on TestPyPI.")
    parser.add_argument("--enable_pypi", action = "store_true", help = "Enable publishing on PyPI.")

    args : Namespace = parser.parse_args()

    return args.enable_testpypi, args.enable_pypi
def create_folder(dir : Path) -> None:
    
    '''Creates dir. Removes pre-existing if it already exists.'''

    if dir.exists():
        shutil.rmtree(dir)
        print(MessageCollection.cleaned_directory(dir))

    dir.mkdir(parents = True, exist_ok = True)

    print(MessageCollection.created_directory(dir))
def create_staging(setting_collection : SettingCollection) -> None:
    
    '''Creates dir_staging. Removes pre-existing if it already exists.'''
    
    create_folder(setting_collection.dir_staging)

    for source_path, destination_path in setting_collection.source_files:
        shutil.copy(source_path, destination_path)
        print(MessageCollection.copied_file(source_path, destination_path))

    source_path, destination_path = setting_collection.readme_file

    if source_path.exists():
        shutil.copy(source_path, destination_path)
        print(MessageCollection.copied_file(source_path, destination_path))
    else:
        print(MessageCollection.file_is_missing(source_path), file=sys.stderr)
def create_dist(setting_collection : SettingCollection) -> None:
    
    '''Creates dir_dist. Removes pre-existing if it already exists.'''

    return create_folder(setting_collection.dir_dist)
def update_setup_file_content(setting_collection : SettingCollection) -> None:

    """Append long_description and long_description_content_type to setup.py in staging."""

    if not setting_collection.setup_file_staging.exists():
        raise FileNotFoundError(MessageCollection.file_is_missing(setting_collection.setup_file_staging))

    if not setting_collection.readme_file[1].exists():
        raise FileNotFoundError(MessageCollection.file_is_missing(setting_collection.readme_file[1]))

    setup_file_content : str = setting_collection.setup_file_staging.read_text(encoding = "utf-8")
    readme_file_content : str = setting_collection.readme_file[1].read_text(encoding = "utf-8")

    injection : str = (
        f',\n        long_description="""{readme_file_content}""",\n'
        '        long_description_content_type="text/markdown"\n    )'
    )

    idx : int = setup_file_content.rfind(")")
    if idx == -1:
        raise RuntimeError(MessageCollection.closing_parenthesis_not_found())

    updated_setup_file_content : str = setup_file_content[:idx] + injection + setup_file_content[idx + 1 :]
    setting_collection.setup_file_staging.write_text(updated_setup_file_content, encoding = "utf-8")
def run_build(setting_collection : SettingCollection) -> None:

    """Build the package against the staging directory."""

    cmd : list[str] = [sys.executable, "-m", "build", str(setting_collection.dir_staging), "--outdir", str(setting_collection.dir_dist)]
    process : CompletedProcess[str] = subprocess.run(cmd, capture_output = True, text = True)

    if process.returncode != 0:
        print(process.stderr, file=sys.stderr)
        raise RuntimeError(MessageCollection.build_failed())
    
    print(MessageCollection.build_successful())
def run_twine_check(setting_collection : SettingCollection) -> None:
    
    """Validate generated packages with twine check."""
    
    dist_files : list[str] = [str(dist_file) for dist_file in setting_collection.dir_dist.glob("*") if dist_file.is_file()]

    if not dist_files:
        raise RuntimeError(MessageCollection.no_dist_files_found())

    cmd : list[str] = [sys.executable, "-m", "twine", "check"] + dist_files
    process : CompletedProcess[str] = subprocess.run(cmd, capture_output=True, text=True)

    if process.stderr:
        print(process.stderr, file=sys.stderr)

    if process.returncode != 0 or "FAILED" in process.stdout or "FAILED" in process.stderr:
        raise RuntimeError(MessageCollection.twine_validation_failed())
    
    print(MessageCollection.twine_validation_successful())
def run_twine_upload_testpypi(setting_collection : SettingCollection) -> None:

    """Upload build artifacts to TestPyPI using twine."""

    dist_files : list[str] = [str(dist_file) for dist_file in setting_collection.dir_dist.glob("*") if dist_file.is_file()]

    if not dist_files:
        raise RuntimeError(MessageCollection.no_dist_files_found())

    cmd : list[str] = [
        sys.executable,
        "-m",
        "twine",
        "upload",
        "--repository",
        "testpypi",
        "-u",
        setting_collection.testpypi_username,
        "-p",
        setting_collection.testpypi_password,
    ] + dist_files

    process : CompletedProcess[str] = subprocess.run(cmd, capture_output = True, text = True)

    if process.stderr:
        print(process.stderr, file=sys.stderr)

    if process.returncode != 0:
        print(process.stdout, file=sys.stdout)
        raise RuntimeError(MessageCollection.twine_upload_testpypi_failed())

    print(MessageCollection.twine_upload_testpypi_successful())
    print(MessageCollection.testpypi_url(setting_collection.project_name))
def run_twine_upload_pypi(setting_collection : SettingCollection) -> None:

    """Upload build artifacts to PyPI using twine."""

    dist_files : list[str] = [str(dist_file) for dist_file in setting_collection.dir_dist.glob("*") if dist_file.is_file()]

    if not dist_files:
        raise RuntimeError(MessageCollection.no_dist_files_found())

    cmd : list[str] = [
        sys.executable,
        "-m",
        "twine",
        "upload",
        "-u",
        setting_collection.pypi_username,
        "-p",
        setting_collection.pypi_password,
    ] + dist_files

    process : CompletedProcess[str] = subprocess.run(cmd, capture_output = True, text = True)

    if process.stderr:
        print(process.stderr, file=sys.stderr)

    if process.returncode != 0:
        print(process.stdout, file=sys.stdout)
        raise RuntimeError(MessageCollection.twine_upload_pypi_failed())

    print(MessageCollection.twine_upload_pypi_successful())
    print(MessageCollection.pypi_url(setting_collection.project_name))

# MAIN
def main():

    check_dependencies()

    try:

        enable_testpypi, enable_pypi = parse_arguments()

        project_name : str = "nwtimetracking"
        setting_collection : SettingCollection = SettingCollectionFactory().create(project_name = project_name)

        create_staging(setting_collection = setting_collection)
        create_dist(setting_collection = setting_collection)
        update_setup_file_content(setting_collection = setting_collection)

        run_build(setting_collection = setting_collection)
        run_twine_check(setting_collection = setting_collection)

        if enable_testpypi:
            run_twine_upload_testpypi(setting_collection = setting_collection)

        if enable_pypi:
            run_twine_upload_pypi(setting_collection = setting_collection)

        if setting_collection.dir_staging.exists():
            shutil.rmtree(setting_collection.dir_staging)
            print(MessageCollection.cleaned_directory(setting_collection.dir_staging))

        print(MessageCollection.publishing_process_completed())

    except Exception as e:
        
        print(MessageCollection.following_exception_raised(e, setting_collection.dir_staging), file = sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()