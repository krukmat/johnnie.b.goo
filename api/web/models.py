import uuid
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model


class Track(Model):
    created_at = columns.DateTime()
    track_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    band = columns.Text(required=True, index=True)
    name = columns.Text(required=True, index=True)
    release = columns.Text(required=True, index=True)
    fp_track_code = columns.Text(required=True, index=True)
    youtube_code = columns.Text(required=True, index=True)