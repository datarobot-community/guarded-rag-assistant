.PHONY: copyright-check apply-copyright fix-licenses check-licenses

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

copyright-check: ## Copyright checks
	docker run -it --rm -v $(CURDIR):/github/workspace apache/skywalking-eyes -c .github/.licenserc.yaml header check

apply-copyright: ## Add copyright notice to new files
	docker run -it --rm -v $(CURDIR):/github/workspace apache/skywalking-eyes -c .github/.licenserc.yaml header fix

fix-licenses: apply-copyright ## Fix licenses

check-licenses: copyright-check ## Check licenses

fix-lint: ## Fix linting issues
	ruff format .
	ruff check . --fix
	mypy --pretty --install-types --non-interactive .

lint: ## Lint the code
	ruff format --check .
	ruff check .
	mypy --pretty --install-types --non-interactive .

check-all: check-licenses lint ## Run all checks
	check-licences
	lint

fix-all: fix-licenses fix-lint ## Fix all issues
