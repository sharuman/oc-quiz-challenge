from setuptools import setup, find_packages

setup(
    name="oc_quiz_challenge",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",    # adjust to your version
        # add other deps here if you have them
    ],
)