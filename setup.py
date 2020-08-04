import setuptools
from setuptools import setup

using_setuptools = True

setup_args = {
    'name': 'NetTraRec',
    'version': '0.0.14',
    'url': 'https://github.com/ga1008/net_tracfic_recorder',
    'description': '服务器流量监控小工具',
    'long_description': open('README.md', encoding="utf-8").read(),
    'author': 'Guardian',
    'author_email': 'zhling2012@live.com',
    'maintainer': 'Guardian',
    'maintainer_email': 'zhling2012@live.com',
    'long_description_content_type': "text/markdown",
    'LICENSE': 'MIT',
    'packages': setuptools.find_packages(),
    'include_package_data': True,
    'zip_safe': False,
    'entry_points': {
        'console_scripts': [
            'netrec = NetRecorder.NetTraRec:record_starter',
            'netrec-server = NetRecorder.NetTraRec:record_starter_server',
        ]
    },

    'classifiers': [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    'install_requires': [
        'basecolors',
        'psutil',
        'redis',
        'requests',
    ],
}

setup(**setup_args)
