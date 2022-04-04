import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'DataPipes',
    version = '1.0.0',
    author="Sean Moore Gonzalez",
    description="Data I/O and PubSub Network for Local & Remote Algorithm Development",
    long_description=long_description,
    url="https://github.com/GeneralInfluence/DataPipes",
    packages = setuptools.find_packages(),
    classifiers=["Data Science :: Algorithm :: Pipeline :: Factory :: Python :: OS Independent"]
)

