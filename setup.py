import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'gdal',
    'numpy',
    'LandsatBasicUtils'
]

setuptools.setup(
    name="Landsat8SimpleAlbedo",
    version="1.0",
    author="Eduard Kazakov",
    author_email="ee.kazakov@gmail.com",
    description="Python class for simple albedo retrieval from Landsat 8 OLI data",
    long_description=long_description,
    keywords='landsat, albedo',
    long_description_content_type="text/markdown",
    url="https://github.com/eduard-kazakov/Landsat8SimpleAlbedo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ],
)