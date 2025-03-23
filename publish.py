#!/usr/bin/env python3
"""
Script to build and publish the package to PyPI.
"""
import os
import subprocess
import sys


def run_command(command):
    """Run a command and return its return code."""
    print(f"Running: {command}")
    return subprocess.call(command, shell=True)


def main():
    """Main function."""
    # Clean previous builds
    if os.path.exists("dist"):
        print("Removing previous builds...")
        run_command("rm -rf dist build *.egg-info")

    # Make sure required packages are installed
    print("Installing build dependencies...")
    run_command("pip install --upgrade pip")
    run_command("pip install --upgrade setuptools wheel twine build")

    # Build the package
    print("Building package...")
    run_command("python -m build")

    # Check the package
    print("Checking package...")
    run_command("twine check dist/*")

    # Upload to PyPI
    print("Uploading package to PyPI...")
    if "--test" in sys.argv:
        run_command("twine upload --repository-url https://test.pypi.org/legacy/ dist/*")
        print("\nPackage uploaded to TestPyPI!")
        print("You can install it with:")
        print("pip install --index-url https://test.pypi.org/simple/ reverse-string-module")
    else:
        run_command("twine upload dist/*")
        print("\nPackage uploaded to PyPI!")
        print("You can install it with:")
        print("pip install reverse-string-module")


if __name__ == "__main__":
    main() 