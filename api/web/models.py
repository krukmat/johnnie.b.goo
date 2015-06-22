import uuid
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
from cassandra.cqlengine.management import create_keyspace, sync_table, create_keyspace_simple

from django.db import connections
from fp import *
from api.web.fp_ext import magic_matches_list


class Track(Model):
    created_at = columns.DateTime()
    track_id = columns.UUID(primary_key=True, default=uuid.uuid4)
    band = columns.Text(required=True, index=True)
    name = columns.Text(required=True, index=True)
    release = columns.Text(required=True, index=True)
    fp_track_code = columns.Text(required=False, index=True)
    youtube_code = columns.Text(required=False, index=True)
    year = columns.Text(required=False, index=True)

    @property
    def echoprint_id(self):
        return str(self.track_id).replace('-', '_')

    @property
    def fpcode(self):
        # TODO: Test
        metadata = metadata_for_track_id(self.echoprint_id)
        fp_code = fp_code_for_track_id(metadata['track_id'])
        return fp_code

    @property
    def similar_to(self):
        # TODO: Improve magic_matches_list
        similar_fingerprints = magic_matches_list(self.fpcode)
        # TODO: Return all Track based on track_id
        # TODO: Reconvert track_id to uuid
        # tracks_ids = [fp['track_id'] for fp in similar_fingerprints]
        # return self.objects.filter()
        return similar_fingerprints



    @classmethod
    def sync(cls, alias='default'):
        connection = connections[alias]
        connection.connect()
        options = connection.settings_dict.get('OPTIONS', {})
        keyspace = connection.settings_dict['NAME']
        replication_opts = options.get('replication', {})
        # strategy_class = replication_opts.pop('strategy_class',
        #                                      'SimpleStrategy')
        replication_factor = replication_opts.pop('replication_factor', 1)
        create_keyspace_simple(keyspace, replication_factor)
        sync_table(cls)