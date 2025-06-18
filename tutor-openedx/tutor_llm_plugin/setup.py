from setuptools import setup, find_packages

setup(
    name="tutor-llm",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "tutor==19.0.3",
        "requests>=2.25.0",
    ],
    entry_points={
        "tutor.plugin.v1": [
            "llm = tutor_llm.plugin"
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Open edX integration for LLM-powered chat functionality",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tutor-llm",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 