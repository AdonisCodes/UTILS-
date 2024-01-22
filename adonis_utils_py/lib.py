from typing import List


def vprint(content: str, verbose: bool=False):
    """
    Context:
        This function implements custom printing logic for verbose output.

    Example:
        vprint('Hello World', verbose=True)

    Output:
        FILE::STDOUT - Hello World
    """
    if verbose:
        print(content)


def ensure_package_installed(parms: List[str], verbose: bool=False) -> List[str]:
    """
    Context:
        This function ensures that a package is installed, and if a version is provided. It ensures it has that version as well!

    Example:
        ensure_package_installed(["openai==1.9.0", "pygame", "matplotlib"])

    Output:
        Returns a list of packages that are not installed.
    """
    not_installed = []
    for package in parms:
        if len(package) == 0:
            continue

        try:
            package_segments = package.split('==')
            package_name = package_segments[0]
            package_version = None
            if len(package_segments) > 1:
                package_version = package_segments[1]

            module = __import__(package_name)
            

            package_version_valid = package_version is None or module.__version__ == package_version

            if package_version_valid:
                vprint(f'[INFO] - Package {package} is installed', verbose)
            else:
                raise ImportError(f'Package {package} is not installed')

        except ImportError:
            not_installed.append(package)
            vprint(f'[ERROR] - Package {package} is not installed', verbose)
    
    return not_installed


def install_packages(parms: List[str], verbose: bool=False) -> None:
    """
    Context:
        This function installs packages with their names & versions ( If specified )

    Example:
        install_packages(["openai==1.9.0", "pygame", "matplotlib"])

    Output:
        Packages are installed which you provided, or errors out if pip errors out.
    """
    for package in parms:
        if len(package) == 0:
            continue

        vprint(f'[INFO] - Installing package {package}', verbose)
        import pip
        pip.main(['install', package])
        vprint(f'[INFO] - Package {package} is installed', verbose)


def ensure_system_dependency_installed(dependencies: List[str], verbose: bool=False) -> List[str]:
    """
    Context:
        This function ensures that a system dependency is installed.

    Example:
        ensure_system_dependency_installed(["ffmpeg"])

    Output:
        Returns a list of system dependencies that are not installed.
    
    Reference:
        https://chat.openai.com/share/b3c5d6ad-adfa-4f73-9a49-e4303d6065ec

    Keywords:
        - 3rd party package
        - ensure installed
        - ensure system dependency installed
        - system dependency
        - system dependency installed
        - snap package
        - snapd
        - snapd install
        - snapd installed
    """

    not_installed = []
    for dependency in dependencies:
        if len(dependency) == 0:
            continue

        try:
            import subprocess
            output = ''
            try:
                output = subprocess.check_output(['which', dependency])
            except:
                not_installed.append(dependency)
                continue

            if len(output) == 0:
                raise ImportError(f'System dependency {dependency} is not installed')

            vprint(f'[INFO] - System dependency {dependency} is installed', verbose)
        except ImportError:
            not_installed.append(dependency)
            vprint(f'[ERROR] - System dependency {dependency} is not installed', verbose)
    return not_installed


def install_3rd_party_dependencies(deps: List[str], verbose: bool=False):
    """
    Context:
        This function installs 3rd party dependencies using snapd.

    Example:
        install_3rd_party_dependencies(["ffmpeg"])

    Output:
        None

    Reference:
        https://chat.openai.com/share/b3c5d6ad-adfa-4f73-9a49-e4303d6065ec
        https://snapcraft.io/docs

    Keywords:
        - 3rd party package
        - ensure installed
        - ensure system dependency installed
        - system dependency
        - system dependency installed
        - snap package
        - snapd
        - snapd install
        - snapd installed
    """
    for dep in deps:
        if len(dep) == 0:
            continue

        vprint(f'[INFO] - Installing 3rd party dependency {dep}', verbose)
        print(f'[INFO] - If this gets stuck somehow, run the script in sudo mode ')
        import subprocess
        subprocess.check_output(['sudo', 'snap', 'install', dep])
        vprint(f'[INFO] - 3rd party dependency {dep} is installed', verbose)

