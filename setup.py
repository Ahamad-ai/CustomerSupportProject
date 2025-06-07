from setuptools import find_packages, setup

setup(name="flipkart-chatbot-ai",
      version="0.0.2",
      author="ahamad",
      author_email="ahamadkv17@gmail.com",
      packages=find_packages(),
      install_requires=["langchain-astradb","langchain"])