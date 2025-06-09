from setuptools import find_packages, setup

setup(
    name="warehouse_automation",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "psycopg2-binary>=2.9",
        "pytest>=7.0",
    ],
    python_requires=">=3.9",
)
