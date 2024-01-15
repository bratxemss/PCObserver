from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('Application.py', base=base)
]

setup(name='PCObserverClient',
      version = '1.0',
      description = 'Client for PCObserver',
      options = {'build_exe': build_options},
      executables = executables)
