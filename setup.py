from setuptools import setup, find_packages

setup(
    name='setup_netns',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyroute2',
    ],
    entry_points='''
        [console_scripts]
        setup-netns=setup_netns.setup_netns:run
    ''',
)
