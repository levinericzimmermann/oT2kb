import setuptools  # type: ignore


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ot2kb",
    license="GPL",
    description="keyboard patch for composition ot2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    url="https://github.com/levinericzimmermann/ot2kb",
    packages=[
        package for package in setuptools.find_packages() if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "mutwo==0.12.0",
        "python-rtmidi==1.4.9",
        "PySimpleGUI==4.46.0",
        "frozendict==2.0.6",
        "natsort==5.5.0",
    ],
    python_requires=">=3.7, <4",
)
