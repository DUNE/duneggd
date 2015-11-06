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
      install_requires = [l for l in open("requirements.txt").readlines() if l.strip()],
      # implicitly depends on ROOT
              
  )

