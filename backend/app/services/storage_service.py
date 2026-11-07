import os
import re
import uuid
import json
import hashlib
import logging
from pathlib import Path
from typing import BinaryIO, List, Optional, Set, Tuple

from app.core.config import settings

logger = logging.getLogger("3d_bharat.storage")

# Supported Media Extensions
MEDIA_ALLOWED_EXTENSIONS: Set[str] = {
    ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff",
    ".pdf",
    ".mp3", ".wav", ".ogg", ".m4a",
    ".mp4", ".webm",
}

# Supported 3D Asset Extensions
ASSET_3D_ALLOWED_EXTENSIONS: Set[str] = {
    ".glb", ".gltf", ".obj", ".mtl", ".ply", ".splat",
}


class StorageService:
    """
    Local file storage abstraction with validation, content-sniffing,
    structural validation for text 3D formats, companion file management,
    path traversal prevention, SHA-256 calculation, and failure recovery.
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

    def validate_file_content(
        self,
        filename: str,
        first_bytes: bytes,
        is_3d: bool = False,
    ) -> Tuple[str, str]:
        """
        Validates file extension, magic byte signatures, and text structure.
        Returns (extension, verified_mime_type).
        """
        ext = os.path.splitext(filename)[1].lower()
        allowed = ASSET_3D_ALLOWED_EXTENSIONS if is_3d else MEDIA_ALLOWED_EXTENSIONS

        if ext not in allowed:
            category = "3D preservation asset" if is_3d else "heritage media"
            raise ValueError(
                f"Unsupported file extension '{ext}' for {category}. "
                f"Allowed extensions: {', '.join(sorted(allowed))}"
            )

        if not first_bytes or len(first_bytes) == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")

        # -------------------------------------------------------------
        # 1. IMAGES & DOCUMENTS
        # -------------------------------------------------------------
        if ext in {".jpg", ".jpeg"}:
            if not first_bytes.startswith(b"\xff\xd8\xff"):
                raise ValueError("Corrupt or invalid JPEG image: missing JPEG header (0xFFD8FF).")
            return ext, "image/jpeg"

        if ext == ".png":
            if not first_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("Corrupt or invalid PNG image: missing PNG magic header.")
            return ext, "image/png"

        if ext == ".webp":
            if not (first_bytes.startswith(b"RIFF") and first_bytes[8:12] == b"WEBP"):
                raise ValueError("Corrupt or invalid WebP image: missing RIFF/WEBP container header.")
            return ext, "image/webp"

        if ext in {".tif", ".tiff"}:
            if not (first_bytes.startswith(b"II*\x00") or first_bytes.startswith(b"MM\x00*")):
                raise ValueError("Corrupt or invalid TIFF image: missing TIFF byte-order header.")
            return ext, "image/tiff"

        if ext == ".pdf":
            if not first_bytes.startswith(b"%PDF-"):
                raise ValueError("Corrupt or invalid PDF document: missing %PDF- header.")
            return ext, "application/pdf"

        # -------------------------------------------------------------
        # 2. AUDIO & VIDEO
        # -------------------------------------------------------------
        if ext == ".mp3":
            is_id3 = first_bytes.startswith(b"ID3")
            is_mpeg_sync = (
                len(first_bytes) >= 2
                and first_bytes[0] == 0xFF
                and (first_bytes[1] & 0xE0) == 0xE0
            )
            if not (is_id3 or is_mpeg_sync):
                raise ValueError("Corrupt or invalid MP3 audio: missing ID3 tag or MPEG frame sync header.")
            return ext, "audio/mpeg"

        if ext == ".wav":
            if not (first_bytes.startswith(b"RIFF") and first_bytes[8:12] == b"WAVE"):
                raise ValueError("Corrupt or invalid WAV audio: missing RIFF/WAVE container header.")
            return ext, "audio/wav"

        if ext == ".ogg":
            if not first_bytes.startswith(b"OggS"):
                raise ValueError("Corrupt or invalid Ogg audio/video: missing OggS container header.")
            return ext, "audio/ogg"

        if ext == ".m4a":
            if not (len(first_bytes) >= 8 and first_bytes[4:8] == b"ftyp"):
                raise ValueError("Corrupt or invalid M4A audio: missing MP4 ftyp container box.")
            return ext, "audio/mp4"

        if ext == ".mp4":
            if not (len(first_bytes) >= 8 and first_bytes[4:8] == b"ftyp"):
                raise ValueError("Corrupt or invalid MP4 video: missing MP4 ftyp container box.")
            return ext, "video/mp4"

        if ext == ".webm":
            if not first_bytes.startswith(b"\x1a\x45\xdf\xa3"):
                raise ValueError("Corrupt or invalid WebM video: missing EBML container header.")
            return ext, "video/webm"

        # -------------------------------------------------------------
        # 3. 3D DIGITAL ASSETS
        # -------------------------------------------------------------
        if ext == ".glb":
            if not first_bytes.startswith(b"glTF"):
                raise ValueError("Corrupt or invalid binary glTF (.glb) model: missing 'glTF' header.")
            return ext, "model/gltf-binary"

        if ext == ".gltf":
            # glTF is JSON; validate structural JSON syntax
            try:
                content_sample = first_bytes.decode("utf-8", errors="replace").strip()
                if not content_sample.startswith("{"):
                    raise ValueError("Malformed glTF: file does not start with JSON object '{'.")
                # Attempt partial parse of JSON chunk or check basic JSON token
                if '"asset"' not in content_sample and '"scenes"' not in content_sample and '"nodes"' not in content_sample:
                    raise ValueError("Malformed glTF: missing glTF standard structure ('asset' metadata).")
            except Exception as e:
                raise ValueError(f"Malformed glTF model JSON structure: {e}")
            return ext, "model/gltf+json"

        if ext == ".obj":
            # Wavefront OBJ is a text-based format containing vertex (v, vn, vt) and face (f) elements
            text_sample = first_bytes.decode("utf-8", errors="replace")
            lines = [line.strip() for line in text_sample.splitlines() if line.strip()]
            valid_obj_prefixes = ("#", "v ", "vn ", "vt ", "f ", "g ", "o ", "mtllib ", "usemtl ", "s ")
            has_obj_token = any(line.startswith(valid_obj_prefixes) for line in lines)
            if not has_obj_token:
                raise ValueError("Malformed Wavefront OBJ: missing standard geometric tokens (v, vn, f, mtllib).")
            return ext, "model/obj"

        if ext == ".mtl":
            # Wavefront Material Library is a text format containing newmtl, Ka, Kd, etc.
            text_sample = first_bytes.decode("utf-8", errors="replace")
            lines = [line.strip() for line in text_sample.splitlines() if line.strip()]
            valid_mtl_prefixes = ("#", "newmtl ", "Ka ", "Kd ", "Ks ", "Ns ", "d ", "illum ", "map_Kd ")
            has_mtl_token = any(line.startswith(valid_mtl_prefixes) for line in lines)
            if not has_mtl_token:
                raise ValueError("Malformed Wavefront Material (.mtl): missing material tokens (newmtl, Ka, Kd).")
            return ext, "text/plain"

        if ext == ".ply":
            # Polygon File Format: starts with 'ply\n'
            if not (first_bytes.startswith(b"ply\n") or first_bytes.startswith(b"ply\r\n")):
                raise ValueError("Corrupt or invalid PLY point cloud: missing 'ply' header line.")
            return ext, "application/x-ply"

        if ext == ".splat":
            # Gaussian Splat format: binary 32-byte chunks (x,y,z, scale, color, rot)
            return ext, "application/octet-stream"

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
        first_chunk = stream.read(4096)
        if not first_chunk:
            raise ValueError("Uploaded file is empty (0 bytes).")

        self.validate_file_content(sanitized, first_chunk, is_3d=is_3d)

        # Generate unique storage key
        unique_id = uuid.uuid4().hex
        ext = os.path.splitext(sanitized)[1].lower()
        storage_rel_dir = Path(category_dir) / f"site_{site_id}" / f"asset_{unique_id}"
        storage_key = f"{storage_rel_dir.as_posix()}/{sanitized}"

        abs_path = self.get_absolute_path(storage_key)
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        sha256 = hashlib.sha256()
        bytes_written = 0

        try:
            with open(abs_path, "wb") as f:
                f.write(first_chunk)
                sha256.update(first_chunk)
                bytes_written += len(first_chunk)
                if bytes_written > max_limit:
                    raise ValueError(
                        f"File size exceeds maximum allowed limit of {max_limit / (1024 * 1024):.1f} MB."
                    )

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

    def save_companion_file(
        self,
        parent_storage_key: str,
        companion_filename: str,
        stream: BinaryIO,
    ) -> Tuple[str, str, int, str]:
        """
        Saves a companion file (e.g. MTL material or texture) into the isolated
        companion directory of a 3D asset: <asset_dir>/companions/<sanitized_name>.
        Guarantees that companion files cannot overwrite or touch unrelated assets.
        """
        parent_path = self.get_absolute_path(parent_storage_key)
        asset_dir = parent_path.parent
        companions_dir = asset_dir / "companions"
        companions_dir.mkdir(parents=True, exist_ok=True)

        sanitized_name = self.sanitize_filename(companion_filename)
        first_chunk = stream.read(4096)
        if not first_chunk:
            raise ValueError("Companion file is empty (0 bytes).")

        # Validate content for companion (can be MTL, image texture, or binary buffer)
        ext = os.path.splitext(sanitized_name)[1].lower()
        if ext in ASSET_3D_ALLOWED_EXTENSIONS:
            self.validate_file_content(sanitized_name, first_chunk, is_3d=True)
        elif ext in MEDIA_ALLOWED_EXTENSIONS:
            self.validate_file_content(sanitized_name, first_chunk, is_3d=False)
        elif ext not in {".bin"}:
            raise ValueError(f"Unsupported companion file extension '{ext}'.")

        target_file = (companions_dir / sanitized_name).resolve()
        # Verify strictly inside companions_dir
        target_file.relative_to(companions_dir)

        sha256 = hashlib.sha256()
        bytes_written = 0

        try:
            with open(target_file, "wb") as f:
                f.write(first_chunk)
                sha256.update(first_chunk)
                bytes_written += len(first_chunk)

                while True:
                    chunk = stream.read(65536)
                    if not chunk:
                        break
                    bytes_written += len(chunk)
                    f.write(chunk)
                    sha256.update(chunk)
        except Exception:
            if target_file.exists():
                try:
                    target_file.unlink()
                except OSError:
                    pass
            raise

        companion_rel_key = target_file.relative_to(self.root_dir).as_posix()
        return companion_rel_key, sanitized_name, bytes_written, sha256.hexdigest()

    def delete_file(self, storage_key: str) -> bool:
        """
        Safely removes file and its asset directory from storage.
        Returns True if deleted or already absent.
        Raises RuntimeError if deletion fails unexpectedly.
        """
        try:
            abs_path = self.get_absolute_path(storage_key)
            if abs_path.exists():
                abs_path.unlink()
                logger.info(f"Deleted storage asset file at {storage_key}")

                # If parent is an asset-specific directory (asset_*), clean up companion folder & dir
                parent = abs_path.parent
                if parent.name.startswith("asset_") and parent.exists():
                    shutil_rm_success = True
                    try:
                        import shutil
                        shutil.rmtree(parent, ignore_errors=False)
                    except Exception as rm_err:
                        logger.error(f"Failed to clean up asset directory {parent}: {rm_err}")
                        shutil_rm_success = False

            if abs_path.exists():
                raise RuntimeError(f"Physical file at {storage_key} could not be deleted.")
            return True
        except Exception as exc:
            logger.error(f"Error deleting file {storage_key}: {exc}")
            raise RuntimeError(f"Storage deletion failed for {storage_key}: {exc}")


storage_service = StorageService()
