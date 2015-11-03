from setuptools import setup


setup(name = 'duneggd',
      version = '0.0',
      description = 'General Geometry Description',
      author = 'Tyler Alion',
      author_email = 'tylerdalion@gmail.com',
      license = 'GPLv2',
      url = 'https://github.com/tyleralion/duneggd',
      package_dir = {'':'python'},
      packages = ['duneggd', 'duneggd.fgt'],
      # These are just what were developed against.  Older versions may be okay.
      #install_requires=[
      #    "pint >= 0.5.1",      # for units
      #    "lxml >= 3.3.5",      # for GDML export
      #],
      install_requires = [l for l in open("requirements.txt").readlines() if l.strip()],
      # implicitly depends on ROOT
      entry_points = {
          'console_scripts': [
              'gegede-cli = gegede.main:main',
              ]
      }
              
  )

