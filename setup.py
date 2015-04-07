from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="tcopy",
    packages=["tcopy"],
    version="0.1.1",
    description="Basic tail call removal decorator",
    long_description=long_description,
    author="Bogdan Popa",
    author_email="popa.bogdanp@gmail.com",
    url="https://github.com/Bogdanp/tcopy",
    keywords=["dangerous", "optimization", "useless"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Interpreters",
    ],
)
