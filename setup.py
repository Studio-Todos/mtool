from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mtool",
    version="0.1.0",
    author="Connor",
    description="A modular CLI tool for various file operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "Pillow>=9.0.0",
        "qrcode[pil]>=7.4.2",
        "requests>=2.25.0",
        "rich>=13.0.0",
        "openai>=1.0.0",
        "pyperclip>=1.8.0",
    ],
    extras_require={
        "audio": ["pydub>=0.25.0"],
        "pdf": ["PyPDF2>=3.0.0", "pdf2image>=1.16.0"],
    },
    entry_points={
        "console_scripts": [
            "mtool=mtool.cli:main",
        ],
    },
) 