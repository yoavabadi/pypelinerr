import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="operation",
    version="0.0.1",
    author="Yoav Abadi",
    author_email="yoavabadi@gmail.com",
    description="A Railway pattern based operation package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yoavabadi/Operation",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
