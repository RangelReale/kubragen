from typing import NewType

TProvider = NewType('TProvider', str)
"""Provider type for the :class:`kubragen.provider.Provider` class."""

TProviderSvc = NewType('TProviderSvc', str)
"""Provider service type for the :class:`kubragen.provider.Provider` class."""

TBuild = NewType('TBuild', str)
"""Build type for the :class:`kubragen.builder.Builder` class."""

TBuildItem = NewType('TBuildItem', str)
"""Build item type for the :class:`kubragen.builder.Builder` class."""
