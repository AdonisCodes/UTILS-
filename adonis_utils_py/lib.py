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
