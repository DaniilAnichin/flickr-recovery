import setuptools

with open("README.md", "r") as out:
    long_description = out.read()

setuptools.setup(
    name="flickr-recovery",
    version="0.0.1",
    author="Daniil Anichyn",
    author_email="daniilanichin@gmail.com",
    description="Python tool to unpack, reorder into albums and rename photos to original names after pooling flick dump",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DaniilAnichin/flickr-recovery",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
