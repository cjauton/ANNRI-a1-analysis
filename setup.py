from setuptools import setup, find_packages

setup(
    name="annri-analysis-framework",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # install_requires=["numpy", "toml", "csv", "pandas"],
    python_requires=">=3.7",
)
