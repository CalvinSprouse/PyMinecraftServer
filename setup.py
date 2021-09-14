from setuptools import setup, find_packages

setup(
    author="Calvin Sprouse",
    author_email="sprousecal@gmail.com",

    name="PyMinecraftServer",
    packages=find_packages(include=["py_minecraft_server"]),
    description="Minecraft Server Management",
    version="0.1.0",

    license="MIT",
    # classifiers=[
    #     "License :: OSI Approved :: MIT License",
    #     "Programming Language :: Python :: 3.9",
    # ],

    include_package_data=True,
    zip_safe=False,

    setup_requires=[None],
    tests_require=[None],
    test_suite="tests",
)
