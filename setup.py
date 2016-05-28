import os
from setuptools import setup, find_packages
setup(
    name = "steam_game_scale",
    version = "1.0.12",
    packages = find_packages(),

    install_requires = ['pillow>=3.2.0','PyYAML>=3.11','requests>=2.9.1'],

    package_data = {
        '': ['*.md', '*.png']
    },
    entry_points='''
      [gui_scripts]
      steam_game_scale=steam_game_scale.__main__:main
    ''',
    author = "Nate Campbell",
    author_email = "nathanc@alum.bu.edu",
    description = "Compare your Steam game playtime against your friends",
    keywords = "steam api friends",
    url = "https://github.com/knbnnate/steam_game_scale/"
)
