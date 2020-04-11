test:
	python -m unittest discover

tester:
	docker run --entrypoint /bin/bash -it --env-file testenv.conf --mount src="$(pwd)",target=/usr/src/app,type=bind mathemagical/banned-word-server

local:
	docker run --entrypoint /bin/bash -it --env-file environment.conf --mount src="$(pwd)",target=/usr/src/app,type=bind mathemagical/banned-word-server