import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='yaml-heritage',
    version='0.0.1',
    author='kyrylo-gr',
    author_email='cryo.paris.su@gmail.com',
    description='Read YAML file into classes.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RemiRousseau/drawable.git',
    license='MIT',
    packages=['yaml_heritage'],
    install_requires=['pyyaml'],
)
