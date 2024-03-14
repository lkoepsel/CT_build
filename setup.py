from setuptools import setup, find_packages

setup(
    name='CT_build',
    version='2.0',
    # This tells setuptools to include any directories, and subdirectories,
    # which include an __init__.py file
    packages=find_packages(),
    install_requires=["pygetwindow>=0.0.9; sys_platform == 'win32'",
                      "pyautogui>=0.9; sys_platform == 'win32'",
                      "click>=8.0",
                      "mpremote>=1.22"],
    entry_points={
        'console_scripts': [
            'ct_conn = utilities.CT_connect:conn',
            'ct_disc = utilities.CT_disconnect:disc',
            'mpbuild = utilities.mpbuild:build',
            'up = utilities.up:up',
        ],
    },
    # Metadata
    author='Lief Koepsel',
    author_email='lkoepsel@wellys.com',
    description='CoolTerm & Sublime Text scripting capabilities',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # Use the URL to the github repo or wherever your code is hosted
    url='https://github.com/lkoepsel/CT_build',
    # Descriptive keywords to help find your package
    keywords='CoolTerm & Sublime Text serial scripting',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        # Pick a topic relevant for your package
        'Topic :: Software Development :: Communications',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        # Specify the Python versions you support here
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
    ],
)
