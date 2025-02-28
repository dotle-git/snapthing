# per-platform functions for code that is platform specific
from abc import ABC, abstractmethod

import subprocess
from io import BytesIO
from typing import override
from shutil import which


class Platform(ABC):
    """
    Abstract class for platform-specific functionality
    """

    @classmethod
    @abstractmethod
    def check_install(cls) -> Exception | None:
        """Validate the installation of external dependencies."""

    @abstractmethod
    def copy_image_to_clipboard(self, image_data: BytesIO) -> None:
        """Copy image to system clipboard"""
        ...

    def assert_dependencies(self):
        error = self.check_install()
        if error is not None:
            raise error


class LinuxXClip(Platform):

    @override
    @classmethod
    def check_install(cls):
        xclip = which('xclip')
        if xclip is None:
            return RuntimeError("xclip is required in order to copy to clipboard")

    @override
    def copy_image_to_clipboard(self, image_data: BytesIO) -> None:
        _ = subprocess.run(
            ['xclip', '-selection', 'clipboard', '-t', 'image/png'], 
            input=image_data.read(), text=False
        )
