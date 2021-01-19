from setuptools import setup

setup(name='savepass',
      version='1.0',
      description='example save pass in keychain',
      author='Vyacheslav Sazanov',
      author_email='slava.sazanov@gmail.com',
      packages=['savepass'],
      install_requires=['paramiko', 'keyring', 'getpass', 'keyrings.alt']
      )
