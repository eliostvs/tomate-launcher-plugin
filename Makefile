PACKAGE = tomate-launcher-plugin
AUTHOR = eliostvs
PACKAGE_ROOT = $(CURDIR)
TOMATE_PATH = $(PACKAGE_ROOT)/tomate
DATA_PATH = $(PACKAGE_ROOT)/data
PLUGIN_PATH = $(DATA_PATH)/plugins
PYTHONPATH = PYTHONPATH=$(TOMATE_PATH):$(PLUGIN_PATH)
DOCKER_IMAGE_NAME = $(AUTHOR)/$(PACKAGE)
PROJECT = home:eliostvs:tomate
DEBUG=TOMATE_DEBUG=true
OBS_API_URL = https://api.opensuse.org:443/trigger/runservice?project=$(PROJECT)&package=$(PACKAGE)

submodule:
	git submodule init
	git submodule update

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf

test: clean
	$(PYTHONPATH) $(DEBUG) py.test tests.py --cov=$(PLUGIN_PATH)

lint:
	flake8

docker-clean:
	docker rmi $(DOCKER_IMAGE_NAME) 2> /dev/null || echo $(DOCKER_IMAGE_NAME) not found!

docker-build:
	docker build -t $(DOCKER_IMAGE_NAME) .

docker-test:
	docker run --rm -v $(PACKAGE_ROOT):/code $(DOCKER_IMAGE_NAME) test

docker-all: docker-clean docker-build docker-test

docker-enter:
	docker run --rm -v $(PACKAGE_ROOT):/code -it --entrypoint="bash" $(DOCKER_IMAGE_NAME)
	
docker-lint:
	docker run --rm -v $(PACKAGE_ROOT):/code $(DOCKER_IMAGE_NAME) lint

trigger-build:
	curl -X POST -H "Authorization: Token $(TOKEN)" $(OBS_API_URL)
