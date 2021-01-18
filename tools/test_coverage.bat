cd ..
coverage run -m --source=. --omit="test\*,setup.py" py.test -v
coverage report
pause