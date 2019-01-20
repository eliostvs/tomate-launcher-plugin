PACKAGE = tomate-launcher-plugin
AUTHOR = eliostvs
PACKAGE_ROOT = $(CURDIR)
TOMATE_PATH = $(PACKAGE_ROOT)/tomate
DATA_PATH = $(PACKAGE_ROOT)/data
PLUGIN_PATH = $(DATA_PATH)/plugins
PYTHONPATH = PYTHONPATH=$(TOMATE_PATH):$(PLUGIN_PATH)
DOCKER_IMAGE_NAME = $(AUTHOR)/$(PACKAGE)
PROJECT = home:eliostvs:tomate
DEBUG = TOMATE_DEBUG=true
OBS_API_URL = https://api.opensuse.org/trigger/runservice
CURRENT_VERSION = `cat .bumpversion.cfg | grep current_version | awk '{print $$3}'`
WORK_DIR = /code

submodule:
	git submodule init;
	git submodule update;

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf

test: clean
	$(PYTHONPATH) $(DEBUG) py.test test_plugin.py --cov=$(PLUGIN_PATH)

docker-clean:
	docker rmi $(DOCKER_IMAGE_NAME) 2> /dev/null || echo $(DOCKER_IMAGE_NAME) not found!

docker-build:
	docker build -t $(DOCKER_IMAGE_NAME) .

docker-test:
	docker run --rm -v $(PACKAGE_ROOT):/code $(DOCKER_IMAGE_NAME) test

docker-all: docker-clean docker-build docker-test

docker-enter:
	docker run --rm -v $(PACKAGE_ROOT):$(WORK_DIR) --workdir $(WORK_DIR) -it --entrypoint="bash" $(DOCKER_IMAGE_NAME)

release-%:
	git flow init -d
	@grep -q '\[Unreleased\]' README.md || (echo 'Create the [Unreleased] section in the changelog first!' && exit)
	bumpversion --verbose --commit $*
	git flow release start $(CURRENT_VERSION)
	GIT_MERGE_AUTOEDIT=no git flow release finish -m "Merge branch release/$(CURRENT_VERSION)" -T $(CURRENT_VERSION) $(CURRENT_VERSION)

trigger-build:
	curl -X POST -H "Authorization: Token $(TOKEN)" $(OBS_API_URL)
