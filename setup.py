from setuptools import find_packages, setup

setup(name="e-commerce-support-bot",
      version="0.0.1",
      author="ahamad",
      author_email="ahamadkv17@gmail.com",
      packages=find_packages(),
      install_requires=["langchain-astradb","langchain"])