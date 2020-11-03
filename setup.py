from setuptools import setup

setup(
    name='app',
    version='1.0',
    long_description=__doc__,
    packages=['app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Click==7.0',
        'Flask==1.0.2',
        'itsdangerous==1.1.0',
        'Jinja2==2.10.1',
        'MarkupSafe==1.1.1',
        'pkg-resources==0.0.0',
        'Werkzeug==0.15.2']
)