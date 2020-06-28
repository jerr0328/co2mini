import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="co2mini",
    version="0.1.0",
    author="Jeremy Mayeres",
    author_email="jeremy@jerr.dev",
    description="Monitor CO2 levels with Prometheus and/or HomeKit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jerr0328/co2-mini",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.6",
    install_requires=["prometheus_client"],
    extras_require={"homekit": ["HAP-python[QRCode]"]},
    entry_points={"console_scripts": ["co2mini = co2mini.main:main"]},
)
