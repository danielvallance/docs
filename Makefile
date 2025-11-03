# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022, Unikraft GmbH and The KraftKit Authors.
# Licensed under the BSD-3-Clause License (the "License").
# You may not use this file except in compliance with the License.

# Directories
WORKDIR ?= $(CURDIR)

# Tools
VALE    ?= vale
WGET    ?= wget
CURL    ?= curl

# Sync configuration
EXAMPLES_REPO     ?= unikraft-cloud/examples
EXAMPLES_BRANCH   ?= main
GUIDES_DIR        ?= $(WORKDIR)/src/guides

.PHONY: lint
lint: $(VALE)
	$(VALE) sync
	$(VALE) $(WORKDIR)/src

.PHONY: $(VALE)
$(VALE):
	@command -v $(VALE) >/dev/null 2>&1 || { \
		echo "❌ $(VALE) is not installed."; \
		echo ""; \
		echo "👉 Please install it before continuing."; \
		echo "   For example:"; \
		echo "     - macOS: brew install $(VALE)"; \
		echo "     - Debian/Ubuntu: snap install $(VALE)"; \
		echo "     - Windows: choco install $(VALE)"; \
		echo "   For more info, visit: https://vale.sh"; \
		exit 1; \
	}

.PHONY: sync
sync:
	@set -e; \
	EXAMPLES_LOCAL="$(WORKDIR)/.examples"; \
	if [ -d "$$EXAMPLES_LOCAL/.git" ]; then \
		cd "$$EXAMPLES_LOCAL" && git fetch --all && git checkout $(EXAMPLES_BRANCH) && git pull; \
	else \
		rm -rf "$$EXAMPLES_LOCAL"; \
		git clone --depth 1 --branch $(EXAMPLES_BRANCH) https://github.com/$(EXAMPLES_REPO) "$$EXAMPLES_LOCAL"; \
	fi; \
	for example in $$(find "$$EXAMPLES_LOCAL" -mindepth 1 -maxdepth 1 -type d -not -name '.*'); do \
		name=$$(basename "$$example"); \
		readme="$$example/README.md"; \
		if [ -f "$$readme" ]; then \
			guide="$(GUIDES_DIR)/$$name.mdx"; \
			echo "  📄 $$name -> $$(basename $$guide)"; \
			$(WORKDIR)/scripts/transform-readme.sh "$$readme" "$$guide" "$$name"; \
		fi; \
	done

.PHONY: sync-list
