import ffripper
from setuptools import setup

data_files = []

setup(
    name = ffripper.__name__,
    packages = [ffripper.__name__],
    scripts = ['bin/ffripper'],
    data_files = data_files,
    version = ffripper.__version__,
    description = ffripper.__description__,
    author = ffripper.__author__,
    author_email = ffripper.__author_email__,
    license = ffripper.__license__,
    platforms = ffripper.__platforms__,
    url = ffripper.__url__,
    download_url = ffripper.__download_url__,
)
