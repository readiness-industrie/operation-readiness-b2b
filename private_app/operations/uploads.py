import hashlib
import io
import zipfile
from pathlib import Path

import filetype
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from .enums import DocumentScanState
from .models import EvidenceDocument

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".xlsx", ".txt", ".csv"}
DETECTED_TYPES = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "txt": "text/plain",
    "csv": "text/csv",
}


def _office_type(raw):
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = set(archive.namelist())
            if "word/document.xml" in names:
                return "docx"
            if "xl/workbook.xml" in names:
                return "xlsx"
    except (zipfile.BadZipFile, OSError):
        return None
    return None


def validate_upload(uploaded, max_bytes):
    original_name = Path(uploaded.name).name[:255]
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("Format refusé. Formats autorisés : PDF, PNG, JPG, DOCX, XLSX, TXT, CSV.")
    if uploaded.size > max_bytes:
        raise ValidationError(f"Fichier trop volumineux (maximum {max_bytes // (1024 * 1024)} Mo).")
    raw = uploaded.read()
    uploaded.seek(0)
    if not raw:
        raise ValidationError("Le fichier est vide.")
    kind = filetype.guess(raw)
    detected = kind.extension if kind else None
    if detected == "zip":
        detected = _office_type(raw)
    if not detected and extension in {".txt", ".csv"}:
        if b"\x00" in raw:
            raise ValidationError("Le contenu ne correspond pas à un fichier texte.")
        try:
            raw.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValidationError("Le fichier texte doit être encodé en UTF-8.") from error
        detected = extension[1:]
    normalized_extension = "jpg" if extension == ".jpeg" else extension[1:]
    if detected != normalized_extension:
        raise ValidationError("Le type réel du fichier ne correspond pas à son extension.")
    return original_name, DETECTED_TYPES[detected], hashlib.sha256(raw).hexdigest()


def create_document(*, uploaded, mission, prerequisite, actor):
    config_max = min(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, __import__("operations.models", fromlist=["BusinessConfig"]).BusinessConfig.get_solo().max_upload_bytes)
    original_name, detected_type, digest = validate_upload(uploaded, config_max)
    document = EvidenceDocument(
        id=__import__("uuid").uuid4(),
        tenant=mission.tenant,
        mission=mission,
        prerequisite=prerequisite,
        file=uploaded,
        original_name=original_name,
        detected_type=detected_type,
        size_bytes=uploaded.size,
        sha256=digest,
        scan_state=DocumentScanState.PENDING if settings.REQUIRE_MALWARE_SCAN else DocumentScanState.SAFE,
        scan_details="En attente d'analyse antivirus" if settings.REQUIRE_MALWARE_SCAN else "Type et contenu validés ; antivirus non requis dans cet environnement",
        uploaded_by=actor,
    )
    document.full_clean()
    document.save()
    return document


def mark_document_shared(document, shared):
    if shared and document.scan_state != DocumentScanState.SAFE:
        raise ValidationError("Le document doit être validé avant partage.")
    document.is_client_shared = shared
    document.shared_at = timezone.now() if shared else None
    document.full_clean()
    document.save(update_fields=["is_client_shared", "shared_at", "updated_at"])
    return document
