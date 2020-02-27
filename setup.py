from setuptools import setup, find_packages

setup(name='donkeypart_t265',
      version='0.1.0',
      description='donkey part for Intel RealSense Tracking Camera T265',
      url='https://github.com/coolerking/donkeypart_t265/',
      author='Tasuku Hori',
      author_email='tasuku-hori@exa-corp.co.jp',
      license='MIT',
      install_requires=['donkeycar', 'pyrealsense2'],

      include_package_data=True,

      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.

          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='donkeycar part intel realsense tracking camera t265 pyrealsense2',

      packages=find_packages(exclude=(['tests', 'assets', 'doc'])),
      )