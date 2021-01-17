cd ..
coverage run -m --source=. --omit="test\*" py.test -v
coverage report
pause