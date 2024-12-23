from setuptools import setup, find_packages

setup(
    name="epidemic_simulator",
    version="0.1.0",
    author="Jose Luis Leiva Fleitas",
    author_email="tuemail@example.com",
    description="A Python library for epidemic simulation using agent-based modeling.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JLeiva44/epidemic_simulator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "matplotlib",
        # Añade otras dependencias aquí
    ],
)
