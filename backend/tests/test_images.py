from app.services.images import ImageKind, ImagePipeline, JobStage


def _decode(url: str) -> str:
    import base64
    return base64.b64decode(url.split(",", 1)[1]).decode().lower()


def test_model_shot_runs_two_stages():
    pipe = ImagePipeline()
    job = pipe.start(b"photo-bytes", ImageKind.MODEL_SHOT)
    assert job.stage is JobStage.REMOVING_BG          # first advance
    job = pipe.poll(job.id)
    assert job.stage is JobStage.DONE                 # second advance
    assert job.image_url.startswith("data:image/svg+xml")
    assert "cut-out" in _decode(job.image_url)        # background-removal ran


def test_packshot_is_not_a_cutout():
    pipe = ImagePipeline()
    job = pipe.start(b"photo-bytes", ImageKind.PACKSHOT)
    assert "cut-out" not in _decode(job.image_url)


def test_packshot_completes_in_one_stage():
    pipe = ImagePipeline()
    job = pipe.start(b"photo-bytes", ImageKind.PACKSHOT)
    assert job.stage is JobStage.DONE
    assert job.status == "completed"
    assert job.image_url.startswith("data:image/svg+xml")


def test_unknown_job_reports_failed():
    pipe = ImagePipeline()
    job = pipe.poll("does-not-exist")
    assert job.status == "failed"


def test_render_is_deterministic():
    a = ImagePipeline().start(b"same-bytes", ImageKind.LIFESTYLE)
    b = ImagePipeline().start(b"same-bytes", ImageKind.LIFESTYLE)
    assert a.image_url == b.image_url
