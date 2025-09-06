from setuptools import setup, find_packages

setup(
    name="xplc",
    version="1.0.0",
    description="AI-powered CLI error explainer",
    long_description="xplc (xplain crash) - Runs commands and explains errors using AI",
    author="Owais Rizvi",
    author_email="owaisrizvi42@gmail.com",
    url="https://github.com/owais-rizvi/xplc",
    py_modules=["xplc"],
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "xplc=xplc:main",
        ],
    }
)