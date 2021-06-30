import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="brfunds",
    version="0.0.3",
    author="Phactos",
    description="Package to scrap data from brazilian funds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Phactos/brfunds",
    project_urls={
        "Bug Tracker": "https://github.com/Phactos/brfunds/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["brfunds"],
    install_requires=['requests','numpy','pandas','bs4'],
    python_requires=">=3.6",
)