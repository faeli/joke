PY_HOME=.tox/py36/bin

init:
	${PY_HOME}/pip install -r requirements-dev.txt
	
test:
	${PY_HOME}/py.test