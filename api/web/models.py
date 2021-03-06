import uuid
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
from cassandra.cqlengine.management import sync_table, create_keyspace_simple
from cassandra.cqlengine import connection
from cassandra.cqlengine.connection import (
    cluster as cql_cluster, session as cql_session)
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import NoHostAvailable

from django.db import connections
from fp import *
from fp_ext import magic_matches_list


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
        similar_tracks = []
        for finger_print in similar_fingerprints:
            try:
                track_id = finger_print['track_id'].split('-')[0].replace('_', '-')
                track = Track.get(track_id=uuid.UUID(track_id))
                if track.pk == self.pk or (track.pk != self.pk and
                                           track in similar_tracks):
                    continue
                similar_tracks.append(track)
            except Exception, exc:
                pass
        return similar_tracks

    @property
    def as_json(self):
        return dict(band=self.band,
                    name=self.name,
                    release=self.release,
                    youtube_code=self.youtube_code,
                    year=self.year)

    @classmethod
    def sync(cls):
        try:
            cassandra_host = connections['default'].settings_dict['HOST'].split(',')
            keyspace = connections['default'].settings_dict['NAME']
            user = connections['default'].settings_dict['USER']
            password = connections['default'].settings_dict['PASSWORD']
            auth_provider = PlainTextAuthProvider(username=user, password=password)

            if cql_cluster is not None:
                cql_cluster.shutdown()
            if cql_session is not None:
                cql_session.shutdown()
            connection.setup(cassandra_host, keyspace, auth_provider=auth_provider)
            sync_table(cls)
        except NoHostAvailable:
            pass