"""
This thing (celery worker) receives tasks
because the DjangoTaskDispatchRepo dispatches them.
It then executes usecases with repos in the usual way.

So think of it like main.py, but for back-end tasks.

Note, it initialises the django config,
but it's not django's normal worker.
There should not be overlap between the task definitions.
Play nice or I'll have to give you your own queues.

TODO:
- there are jobs dispatching tasks that don't exist yet.
- for example, calling the web callbacks
- we need tasks wrappers for this
- it needs error and success messages.
  (should we be signing them?)
- maybe it goes via the action service?
  (because networking, maybe we have no direct internet)

"""

from __future__ import absolute_import, unicode_literals

from celery import Celery
from django_setup import setup_django

# Set up Django before importing anything that depends on Django
setup_django()

# Now we can safely import Django-dependent modules
import usecases  # noqa

from config import reposet  # noqa

app = Celery("knowledge_service")
app.config_from_object("django.conf:settings", namespace="CELERY")


@app.task
def initiate_processing_of_new_resource(resource_id: str) -> None:
    """Initiate processing of a new resource."""
    uc = usecases.InitiateProcessingOfNewResource(reposet)
    return uc.execute(resource_id)


@app.task
def initiate_resource_graph(resource_id: str) -> None:
    """Initialize resource graph."""
    uc = usecases.InitialiseResourceGraph(reposet)
    return uc.execute(resource_id)


@app.task
def extract_plain_text_of_resource(resource_id: str) -> None:
    """Extract plain text from resource."""
    uc = usecases.ExtractPlainTextOfResource(reposet)
    return uc.execute(resource_id)


@app.task
def chunk_resource_text(resource_id: str) -> None:
    """Chunk resource text into segments."""
    uc = usecases.ChunkResourceText(reposet)
    return uc.execute(resource_id)


@app.task
def update_chunks_with_embeddings(resource_id: str) -> None:
    """Update chunks with embeddings."""
    uc = usecases.UpdateChunksWithEmbeddings(reposet)
    return uc.execute(resource_id)


@app.task
def ventilate_resource_processing(resource_id: str) -> None:
    """Ventilate resource processing."""
    uc = usecases.VentilateResourceProcessing(reposet)
    return uc.execute(resource_id)
