from setuptools import find_packages, setup

setup(
    name="medical_chatbot",
    version="0.1.0",
    author="Disha Dasgupta",
    author_email="dishadasgupta7602@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[]
)