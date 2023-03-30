from setuptools import setup, find_packages
setup(
    use_scm_version={
        'write_to': 'src/curitz/version.py',
    },
    setup_requires=['setuptools_scm'],
    install_requires=['zinolib<0.10'],
    name='curitz',
    author='Runar Borge',
    author_email='runar.borge@uninett.no',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
    url=[''],
    license='LISENSE.txt',
    description="Python curses interface to Zino",
    long_description=open('README.md').read(),
    include_package_data=True,
    scripts=['bin/curitz'],
    extras_require = {
        'DNS':  ["dnspython"]
    },
)
