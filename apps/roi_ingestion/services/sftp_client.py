from __future__ import annotations

import logging
import os
import socket
import time
from pathlib import Path
from typing import Iterable

from django.conf import settings

logger = logging.getLogger(__name__)


class SftpClientError(RuntimeError):
    pass


class RoiSftpClient:
    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
        private_key: str | None = None,
        remote_dir: str | None = None,
        archive_dir: str | None = None,
        retries: int = 3,
        retry_delay_seconds: float = 2.0,
    ):
        self.host = host or getattr(settings, "SFTP_HOST", os.getenv("SFTP_HOST", ""))
        self.port = int(port or getattr(settings, "SFTP_PORT", os.getenv("SFTP_PORT", 22)))
        self.username = username or getattr(settings, "SFTP_USERNAME", os.getenv("SFTP_USERNAME", ""))
        self.password = password or getattr(settings, "SFTP_PASSWORD", os.getenv("SFTP_PASSWORD", ""))
        self.private_key = private_key or getattr(settings, "SFTP_PRIVATE_KEY", os.getenv("SFTP_PRIVATE_KEY", ""))
        self.remote_dir = remote_dir or getattr(settings, "SFTP_REMOTE_DIR", os.getenv("SFTP_REMOTE_DIR", "."))
        self.archive_dir = archive_dir or getattr(settings, "SFTP_ARCHIVE_DIR", os.getenv("SFTP_ARCHIVE_DIR", ""))
        self.retries = retries
        self.retry_delay_seconds = retry_delay_seconds
        self._transport = None
        self._sftp = None

    def __enter__(self) -> "RoiSftpClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def connect(self) -> None:
        try:
            import paramiko
        except ImportError as exc:
            raise SftpClientError("Paramiko is required for ROI SFTP ingestion") from exc

        if not self.host or not self.username:
            raise SftpClientError("SFTP_HOST and SFTP_USERNAME are required")

        last_exc: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                transport = paramiko.Transport((self.host, self.port))
                pkey = None
                if self.private_key:
                    pkey = paramiko.RSAKey.from_private_key_file(self.private_key)
                transport.connect(username=self.username, password=self.password or None, pkey=pkey)
                self._transport = transport
                self._sftp = paramiko.SFTPClient.from_transport(transport)
                return
            except (OSError, socket.error, Exception) as exc:
                last_exc = exc
                logger.warning("SFTP connection attempt %s failed: %s", attempt, exc.__class__.__name__)
                if attempt < self.retries:
                    time.sleep(self.retry_delay_seconds * attempt)
        raise SftpClientError("Could not connect to SFTP server") from last_exc

    def close(self) -> None:
        if self._sftp:
            self._sftp.close()
        if self._transport:
            self._transport.close()
        self._sftp = None
        self._transport = None

    @property
    def sftp(self):
        if self._sftp is None:
            self.connect()
        return self._sftp

    def list_files(self) -> list[str]:
        return [item.filename for item in self.sftp.listdir_attr(self.remote_dir) if not str(item.filename).startswith(".")]

    def file_size(self, file_name: str) -> int:
        remote_path = self._remote_path(file_name)
        return int(self.sftp.stat(remote_path).st_size)

    def list_file_sizes(self, file_names: Iterable[str]) -> dict[str, int]:
        sizes: dict[str, int] = {}
        for file_name in file_names:
            try:
                sizes[file_name] = self.file_size(file_name)
            except Exception as exc:
                logger.warning("Could not read remote file size for %s: %s", file_name, exc.__class__.__name__)
        return sizes

    def download_file(self, file_name: str, local_dir: Path) -> Path:
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = local_dir / file_name
        self.sftp.get(self._remote_path(file_name), str(local_path))
        return local_path

    def archive_file(self, file_name: str) -> None:
        if not self.archive_dir:
            return
        source = self._remote_path(file_name)
        target = f"{self.archive_dir.rstrip('/')}/{file_name}"
        self.sftp.rename(source, target)

    def _remote_path(self, file_name: str) -> str:
        return f"{self.remote_dir.rstrip('/')}/{file_name}"
