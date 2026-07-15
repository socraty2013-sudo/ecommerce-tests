from setuptools import setup, find_packages

setup(
    name="ecommerce-tests",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "allure-pytest",
        "playwright",
        "requests",
        "Flask",
        "pytest-cov",
        "pytest-rerunfailures",
        "pytest-xdist",
    ],
)
