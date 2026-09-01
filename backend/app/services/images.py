from __future__ import annotations

import abc
import base64
import hashlib
import time
import uuid
from enum import StrEnum
from threading import Lock

from pydantic import BaseModel, Field, computed_field


class ImageKind(StrEnum):
    MODEL_SHOT = "model_shot"
    LIFESTYLE = "lifestyle"
    PACKSHOT = "packshot"

_NEEDS_BG_REMOVAL = {ImageKind.MODEL_SHOT}

class JobStage(StrEnum):
    GENERATING = "generating"
    REMOVING_BG = "removing_bg"
    DONE = "done"
    FAILED = "failed"

class ImageJob(BaseModel):
    id: str
    kind: ImageKind
    stage: JobStage
    image_url: str | None = None
    error: str | None = None
    created_at: float = Field(default_factory=time.time)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def status(self) -> str:
        if self.stage is JobStage.DONE:
            return "completed"
        if self.stage is JobStage.FAILED:
            return "failed"
        return "processing"

class JobStore(abc.ABC):
    @abc.abstractmethod
    def get(self, job_id: str) -> ImageJob | None: ...

    @abc.abstractmethod
    def put(self, job: ImageJob) -> None: ...

    @abc.abstractmethod
    def evict_older_than(self, max_age_seconds: float) -> None: ...

class InMemoryJobStore(JobStore):
    def __init__(self) -> None:
        self._jobs: dict[str, ImageJob] = {}
        self._lock = Lock()

    def get(self, job_id: str) -> ImageJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def put(self, job: ImageJob) -> None:
        with self._lock:
            self._jobs[job.id] = job

    def evict_older_than(self, max_age_seconds: float) -> None:
        cutoff = time.time() - max_age_seconds
        with self._lock:
            self._jobs = {
                k: v for k, v in self._jobs.items() if v.created_at >= cutoff
            }

class ImageProvider(abc.ABC):
    @abc.abstractmethod
    def render(self, source_image: bytes, kind: ImageKind, prompt: str) -> str: ...

    @abc.abstractmethod
    def remove_background(self, image_url: str) -> str: ...

_STUDIO = {
    ImageKind.MODEL_SHOT: ("#f1f2f6", "#e2e4ec"),
    ImageKind.LIFESTYLE: ("#eef2ef", "#dde7e0"),
    ImageKind.PACKSHOT: ("#f4f3f0", "#eae8e2"),
}
_GARMENT = {"base": "#59698a", "shade": "#4a586f", "light": "#7181a1", "seam": "#3b4760"}

def _jacket_unit() -> str:
    g = _GARMENT
    return (
        f'<path d="M120 30 36 84 60 250 128 150Z" fill="{g["shade"]}"/>'
        f'<path d="M240 30 324 84 300 250 232 150Z" fill="{g["shade"]}"/>'
        f'<path d="M120 30C150 16 210 16 240 30L252 130C256 250 250 360 236 452'
        f'L124 452C110 360 104 250 108 130Z" fill="{g["base"]}"/>'
        '<path d="M180 40 252 130C256 250 250 360 236 452L180 452Z" '
        'fill="#0b1220" fill-opacity="0.12"/>'
        f'<path d="M144 22 180 12 216 22 200 52 180 34 160 52Z" fill="{g["light"]}"/>'
        f'<line x1="180" y1="34" x2="180" y2="452" stroke="{g["seam"]}" stroke-width="3"/>'
        f'<circle cx="180" cy="48" r="4" fill="{g["seam"]}"/>'
        f'<line x1="124" y1="452" x2="236" y2="452" stroke="{g["light"]}" stroke-width="2"/>'
    )

def _mannequin() -> str:
    return (
        '<ellipse cx="381" cy="922" rx="80" ry="14" fill="#c3c8d2"/>'
        '<rect x="374" y="560" width="14" height="362" fill="#c8ccd5"/>'
        '<rect x="361" y="150" width="40" height="46" rx="7" fill="#ccd1db"/>'
        '<path d="M300 214C300 172 336 150 381 150C426 150 462 172 462 214'
        'C471 310 452 470 430 566L332 566C310 470 291 310 300 214Z" fill="#d2d6df"/>'
        '<path d="M381 150C426 150 462 172 462 214C471 310 452 470 430 566'
        'L381 566Z" fill="#0b1220" fill-opacity="0.08"/>'
    )

def _compose(kind: ImageKind, *, cutout: bool) -> str:
    if cutout:
        checker = (
            '<pattern id="t" width="92" height="92" patternUnits="userSpaceOnUse">'
            '<rect width="92" height="92" fill="#ffffff"/>'
            '<rect width="46" height="46" fill="#f5f6f8"/>'
            '<rect x="46" y="46" width="46" height="46" fill="#f5f6f8"/></pattern>'
        )
        return (
            f'<defs>{checker}'
            '<filter id="s" x="-30%" y="-30%" width="160%" height="160%">'
            '<feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#0b1220" '
            'flood-opacity="0.16"/></filter></defs>'
            '<rect width="762" height="1100" fill="url(#t)"/>'
            f'<g transform="translate(191 210) scale(1.06)" filter="url(#s)">'
            f'{_jacket_unit()}</g>'
        )

    top, bottom = _STUDIO[kind]
    defs = (
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/>'
        '</linearGradient>'
        '<filter id="s" x="-30%" y="-30%" width="160%" height="160%">'
        '<feDropShadow dx="0" dy="18" stdDeviation="20" flood-color="#0b1220" '
        'flood-opacity="0.12"/></filter></defs>'
        '<rect width="762" height="1100" fill="url(#bg)"/>'
    )

    if kind is ImageKind.PACKSHOT:
        return (
            defs
            + '<ellipse cx="381" cy="768" rx="150" ry="20" fill="#0b1220" '
            'fill-opacity="0.06"/>'
            f'<g transform="translate(170 196) scale(1.17)" filter="url(#s)">'
            f'{_jacket_unit()}</g>'
        )

    if kind is ImageKind.LIFESTYLE:
        return (
            defs
            + '<circle cx="580" cy="300" r="66" fill="#e9eee9"/>'
            '<path d="M0 590C180 520 320 585 470 545C590 513 690 560 762 532'
            'V1100H0Z" fill="#d4ddd4"/>'
            '<path d="M0 700C170 640 330 690 470 650C600 616 700 680 762 650'
            'V1100H0Z" fill="#c6d0c7"/>'
            '<path d="M0 815C230 765 400 812 560 785C660 768 720 800 762 792'
            'V1100H0Z" fill="#b8c5bb"/>'
            '<ellipse cx="292" cy="834" rx="62" ry="10" fill="#0b1220" fill-opacity="0.07"/>'
            '<path d="M262 700 250 828 272 828 286 720Z" fill="#8a9382"/>'
            '<path d="M300 700 316 826 336 826 322 712Z" fill="#7e8778"/>'
            '<circle cx="288" cy="524" r="20" fill="#ccd1db"/>'
            '<rect x="281" y="540" width="14" height="14" fill="#c2c7d1"/>'
            '<path d="M250 566C250 552 262 544 288 544C314 544 326 552 326 566'
            'L332 690C332 704 320 712 288 712C256 712 244 704 244 690Z" fill="#59698a"/>'
            '<path d="M288 544C314 544 326 552 326 566L332 690C332 704 320 712 288 712Z" '
            'fill="#0b1220" fill-opacity="0.12"/>'
            '<path d="M326 574 352 660 338 668 312 590Z" fill="#4a586f"/>'
        )

    return (
        defs
        + '<rect y="786" width="762" height="314" fill="#dadde5"/>'
        '<ellipse cx="381" cy="930" rx="152" ry="24" fill="#0b1220" fill-opacity="0.05"/>'
        + _mannequin()
        + f'<g transform="translate(201 150)" filter="url(#s)">{_jacket_unit()}</g>'
    )


def _placeholder_svg(kind: ImageKind, token: str, *, cutout: bool = False) -> str:
    """A deterministic 762x1100 editorial "render" as an inline SVG data URI."""
    mark = f"mock render {token} cut-out" if cutout else f"mock render {token}"
    tag = (
        ('<g opacity="0.5"><rect x="40" y="40" width="118" height="30" rx="6" fill="#191e28"/>'
         '<text x="99" y="60" text-anchor="middle" font-family="ui-monospace,monospace" '
         'font-size="14" letter-spacing="2" fill="#ffffff">CUT-OUT</text></g>')
        if cutout
        else
        ('<g opacity="0.5"><rect x="636" y="40" width="86" height="30" rx="6" fill="#191e28"/>'
         '<text x="679" y="60" text-anchor="middle" font-family="ui-monospace,monospace" '
         'font-size="14" letter-spacing="2" fill="#ffffff">DEMO</text></g>')
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="762" height="1100" '
        'viewBox="0 0 762 1100">'
        f'{_compose(kind, cutout=cutout)}'
        f'{tag}'
        f'<text x="722" y="1066" text-anchor="end" font-family="ui-monospace,monospace" '
        f'font-size="15" fill="#0b1220" fill-opacity="0.22">{mark}</text>'
        '</svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


class MockImageProvider(ImageProvider):
    def render(self, source_image: bytes, kind: ImageKind, prompt: str) -> str:
        token = hashlib.sha1(
            f"{kind}:{prompt}:{len(source_image)}".encode()
        ).hexdigest()[:8]
        return _placeholder_svg(kind, token)

    def remove_background(self, image_url: str) -> str:
        token = hashlib.sha1(image_url.encode()).hexdigest()[:8]
        return _placeholder_svg(ImageKind.MODEL_SHOT, token, cutout=True)

_JOB_MAX_AGE = 24 * 60 * 60
_PROMPTS = {
    ImageKind.MODEL_SHOT: "full-body model wearing this exact garment, studio lighting",
    ImageKind.LIFESTYLE: "model wearing this exact garment in a natural setting",
    ImageKind.PACKSHOT: "the garment only, isolated on a clean white background",
}

class ImagePipeline:
    def __init__(
        self,
        provider: ImageProvider | None = None,
        store: JobStore | None = None,
    ) -> None:
        self.provider = provider or MockImageProvider()
        self.store = store or InMemoryJobStore()

    def start(self, source_image: bytes, kind: ImageKind) -> ImageJob:
        self.store.evict_older_than(_JOB_MAX_AGE)
        url = self.provider.render(source_image, kind, _PROMPTS[kind])
        job = ImageJob(
            id=uuid.uuid4().hex,
            kind=kind,
            stage=JobStage.GENERATING,
            image_url=url,
        )
        self.store.put(job)
        return self._advance(job)

    def poll(self, job_id: str) -> ImageJob:
        job = self.store.get(job_id)
        if job is None:
            return ImageJob(
                id=job_id, kind=ImageKind.PACKSHOT, stage=JobStage.FAILED,
                error="unknown job",
            )
        return self._advance(job)

    def _advance(self, job: ImageJob) -> ImageJob:
        if job.stage is JobStage.GENERATING:
            if job.kind in _NEEDS_BG_REMOVAL:
                job.stage = JobStage.REMOVING_BG
                job.image_url = self.provider.remove_background(job.image_url or "")
            else:
                job.stage = JobStage.DONE
        elif job.stage is JobStage.REMOVING_BG:
            job.stage = JobStage.DONE
        self.store.put(job)
        return job
pipeline = ImagePipeline()