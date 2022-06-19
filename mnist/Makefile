
MAKEFILE_DIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
REPOGITORY=takumi2786
NAME=mnist-runner
SRC_PATH=/app/train.py


docker/build:
	docker build -t ${REPOGITORY}/${NAME} .

docker/run:
	docker run ${REPOGITORY}/${NAME} python ${SRC_PATH}

docker/shell:
	docker run -it -v ${MAKEFILE_DIR}:/app ${REPOGITORY}/${NAME}  /bin/bash

docker/push:
	docker push ${REPOGITORY}/${NAME}