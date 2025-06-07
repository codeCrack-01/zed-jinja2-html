#!/usr/bin/env python3
"""
Setup script for Jinja2 HTML Language Server
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = ""
readme_file = here.parent / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="jinja2-html-lsp",
    version="0.1.0",
    description="Language Server Protocol implementation for Jinja2 HTML templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/zed-jinja2-html",
    author="Jinja2 HTML LSP Contributors",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Editors :: Integrated Development Environments (IDE)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="jinja2, html, language-server, lsp, template, completion, zed",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pygls>=1.0.0",
        "lsprotocol>=2023.0.0",
        "jinja2>=3.1.0",
        "markupsafe>=2.1.0",
        "beautifulsoup4>=4.12.0",
        "html5lib>=1.1",
        "regex>=2023.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "mypy>=1.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "formatting": [
            "black>=23.0.0",
            "prettier>=0.0.7",
        ],
    },
    entry_points={
        "console_scripts": [
            "jinja2-html-lsp=main:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/zed-jinja2-html/issues",
        "Source": "https://github.com/yourusername/zed-jinja2-html",
        "Documentation": "https://github.com/yourusername/zed-jinja2-html/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)