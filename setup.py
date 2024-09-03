from setuptools import setup, find_packages

setup(
    name='commitly_api',
    version='0.1.0',
    description='A short description of your project',
    author='Joan Arau',
    author_email='arau.j@zinnfiguren.de',
    url='https://github.com/Wilhelm-Schweizer/commitly_api',  # Replace with your project's URL
    packages=find_packages(),  # Automatically find and include all packages in your project
    install_requires=[
        # List your project's dependencies here, e.g.:
        # 'requests>=2.20.0',
        # 'numpy>=1.18.0',
    ],
    python_requires='>=3.6',  # Specify the Python versions supported
)