import os
import re
import uuid
import hashlib
import logging
from pathlib import Path
from typing import BinaryIO, Optional, Set, Tuple

from app.core.config import settings

logger = logging.getLogger("3d_bharat.storage")

# Supported Media Extensions & MIME types
MEDIA_ALLOWED_EXTENSIONS: Set[str] = {
    ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff",
    ".pdf",
    ".mp3", ".wav", ".ogg", ".m4a",
    ".mp4", ".webm",
}

# Supported 3D Asset Extensions & MIME types
ASSET_3D_ALLOWED_EXTENSIONS: Set[str] = {
    ".glb", ".gltf", ".obj", ".mtl", ".ply", ".splat",
}

# Magic byte signatures for content sniffing
MAGIC_SIGNATURES = [
    (b"\xff\xd8\xff", {".jpg", ".jpeg"}, "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", {".png"}, "image/png"),
    (b"%PDF", {".pdf"}, "application/pdf"),
    (b"glTF", {".glb"}, "model/gltf-binary"),
    (b"RIFF", {".webp", ".wav"}, None),  # WebP or WAV container
    (b"OggS", {".ogg"}, "audio/ogg"),
    (b"ply\n", {".ply"}, "application/x-ply"),
    (b"ply\r\n", {".ply"}, "application/x-ply"),
]


class StorageService:
    """
    Local file storage abstraction with validation, path traversal prevention,
    SHA-256 calculation, and cleanup of failed operations.
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = (root_dir or settings.STORAGE_LOCAL_ROOT).resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        """
        Strips path components, prevents traversal, and replaces unsafe characters.
        """
        base = os.path.basename(filename).strip()
        # Remove any path separators and null bytes
        base = base.replace("/", "").replace("\\", "").replace("\x00", "")
        # Retain only safe alphanumeric characters, dashes, underscores, and dots
        sanitized = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base)
        # Prevent hidden files or empty names
        sanitized = sanitized.lstrip(".")
        if not sanitized:
            sanitized = f"asset_{uuid.uuid4().hex[:8]}"
        return sanitized

    def validate_media_type(
        self,
        filename: str,
        first_bytes: bytes,
        is_3d: bool = False,
    ) -> Tuple[str, str]:
        """
        Validates file extension and sniffs header magic bytes.
        Returns (extension, derived_or_checked_mime).
        """
        ext = os.path.splitext(filename)[1].lower()
        allowed = ASSET_3D_ALLOWED_EXTENSIONS if is_3d else MEDIA_ALLOWED_EXTENSIONS

        if ext not in allowed:
            category = "3D preservation asset" if is_3d else "heritage media"
            raise ValueError(
                f"Unsupported file extension '{ext}' for {category}. "
                f"Allowed extensions: {', '.join(sorted(allowed))}"
            )

        # Content sniffing where signature is available
        for signature, matching_exts, mime in MAGIC_SIGNATURES:
            if first_bytes.startswith(signature):
                if ext not in matching_exts:
                    raise ValueError(
                        f"File header signature does not match extension '{ext}'."
                    )
                return ext, mime or "application/octet-stream"

        # Text-based formats (OBJ, MTL, GLTF JSON) or formats without strict fixed magic prefix
        return ext, "application/octet-stream"

    def get_absolute_path(self, storage_key: str) -> Path:
        """
        Resolves storage key to absolute filesystem path and guards against path traversal.
        """
        normalized_key = storage_key.strip().replace("\\", "/").lstrip("/")
        if ".." in normalized_key:
            raise ValueError("Path traversal detected in storage key.")

        target = (self.root_dir / normalized_key).resolve()
        try:
            # Ensure target is strictly inside root_dir
            target.relative_to(self.root_dir)
        except ValueError:
            raise ValueError("Resolved path is outside authorized storage root.")

        return target

    def save_file_stream(
        self,
        stream: BinaryIO,
        original_filename: str,
        category_dir: str,
        site_id: int,
        is_3d: bool = False,
        max_bytes: Optional[int] = None,
    ) -> Tuple[str, str, int, str]:
        """
        Streams binary data into storage, computing SHA-256 and enforcing file size.
        Returns (storage_key, sanitized_filename, file_size_bytes, sha256_checksum).
        """
        sanitized = self.sanitize_filename(original_filename)
        max_limit = max_bytes or (
            settings.MAX_3D_FILE_SIZE_BYTES if is_3d else settings.MAX_MEDIA_FILE_SIZE_BYTES
        )

        # Read first chunk for header validation
        first_chunk = stream.read(1024)
        if not first_chunk:
            raise ValueError("Uploaded file is empty (0 bytes).")

        self.validate_media_type(sanitized, first_chunk, is_3d=is_3d)

        # Generate unique storage key
        unique_id = uuid.uuid4().hex
        ext = os.path.splitext(sanitized)[1].lower()
        storage_rel_dir = Path(category_dir) / f"site_{site_id}"
        storage_key = f"{storage_rel_dir.as_posix()}/{unique_id}_{sanitized}"

        abs_path = self.get_absolute_path(storage_key)
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        sha256 = hashlib.sha256()
        bytes_written = 0

        try:
            with open(abs_path, "wb") as f:
                f.write(first_chunk)
                sha256.update(first_chunk)
                bytes_written += len(first_chunk)

                while True:
                    chunk = stream.read(65536)
                    if not chunk:
                        break
                    bytes_written += len(chunk)
                    if bytes_written > max_limit:
                        raise ValueError(
                            f"File size exceeds maximum allowed limit of {max_limit / (1024 * 1024):.1f} MB."
                        )
                    f.write(chunk)
                    sha256.update(chunk)
        except Exception:
            # Cleanup on failure to prevent orphaned partial files
            if abs_path.exists():
                try:
                    abs_path.unlink()
                except OSError as cleanup_err:
                    logger.warning(f"Failed to remove partial file {abs_path}: {cleanup_err}")
            raise

        return storage_key, sanitized, bytes_written, sha256.hexdigest()

    def delete_file(self, storage_key: str) -> bool:
        """
        Safely removes file from storage. Returns True if deleted or already absent.
        """
        try:
            abs_path = self.get_absolute_path(storage_key)
            if abs_path.exists():
                abs_path.unlink()
                logger.info(f"Deleted storage asset at {storage_key}")
            return True
        except Exception as exc:
            logger.error(f"Error deleting file {storage_key}: {exc}")
            return False


storage_service = StorageService()
