# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022, Unikraft GmbH and The KraftKit Authors.
# Licensed under the BSD-3-Clause License (the "License").
# You may not use this file except in compliance with the License.

# Directories
WORKDIR ?= $(CURDIR)

# Tools
VALE    ?= vale

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
