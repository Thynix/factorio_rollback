from setuptools import setup

setup(
    name='Factorio Autosave Rollback',
    version='0.1',
    packages=['factorio_rollback'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['flask-wtf']
)
