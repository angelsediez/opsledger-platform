.PHONY: help tree

help:
	@echo "Available targets:"
	@echo "  tree  - Show repository structure"

tree:
	@tree -a -I '.git|.venv|__pycache__|.pytest_cache'
