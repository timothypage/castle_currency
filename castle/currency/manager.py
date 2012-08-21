from itertools import izip_longest

from django.db import connections, models
from django.db.models.query import QuerySet
from django.db.models.sql.query import Query
from django.db.models.sql.where import AND, Constraint


CHUNK_SIZE = 900 # TODO could be safely set at 999

def chunk_list(n, iterable):
    """
    From: http://stackoverflow.com/questions/1624883/alternative-way-to-split-a-list-into-groups-of-n
    """
    args = [iter(iterable)] * n
    return ([e for e in t if e != None] for t in izip_longest(*args))


class BulkDeleteQuery(Query):
    """
    """
    compiler = 'SQLDeleteCompiler'

    # TODO what's necessary here?
    def do_query(self, table, where, using):
        self.tables = [table]
        self.where = where
        self.get_compiler(using).execute_sql(None)

    def delete_ids(self, pk_list, using):
        """
        """
        field = self.model._meta.pk
        where = self.where_class()
        where.add((Constraint(None, field.column, field), 'in', pk_list), AND)
        self.do_query(self.model._meta.db_table, where, using=using)


class VortexQuerySet(QuerySet):
    """
    """
    def bulk_create(self, objs):
        """
        Sugar on top of bulk_create to prevent SQLite parameter overload.
        """
        # TODO guarantee existance of this feature?
        if connections[self.db].features.supports_1000_query_parameters:
            # Call the parent method
            super(VortexQuerySet, self).bulk_create(objs)
        else:
            # Chunk into groups and create
            # Determine the number of fields
            num_fields = len(self.model._meta.fields)
            
            # Determine the maximum object chunk size
            obj_chunk_size = CHUNK_SIZE / num_fields
            
            for obj_chunk in chunk_list(obj_chunk_size, objs):
                super(VortexQuerySet, self).bulk_create(obj_chunk)
    
    
    def bulk_delete(self, id_list):
        """
        Bulk delete objects by primary key.
        No signals are sent and relations are ignored.
        """
        # TODO how to accept current query?
        assert self.query.can_filter(), "Cannot use 'limit' or 'offset' with bulk_delete"
        if not id_list:
            return

        # TODO guarantee existance of this feature?
        if connections[self.db].features.supports_1000_query_parameters:
            # Call the local version of delete (non-chunking)        
            query = BulkDeleteQuery(self.model)
            query.delete_ids(id_list, self.db)
        else:
            # Chunk into groups and delete
            for id_chunk in chunk_list(CHUNK_SIZE, id_list):
                query = BulkDeleteQuery(self.model)
                query.delete_ids(id_chunk, self.db)
            
        self._result_cache = None
    
    bulk_delete.alters_data = True
    

    def in_bulk(self, id_list=None, key='id'):
        """
        A shitty implementation of https://code.djangoproject.com/ticket/8065
        """      
        # TODO assertions for the key? Must be a field? unique?
        assert self.query.can_filter(), "Cannot use 'limit' or 'offset' with in_bulk"
        
        qs = self._clone()
        
        if id_list is not None:
            if not id_list:
                return {}
        
            qs.query.add_filter(('pk__in', id_list))
        
        qs.query.clear_ordering(force_empty=True)

        # TODO use obj._get_pk_val() ?
        return {getattr(obj, key): obj for obj in qs}
        

class VortexManager(models.Manager):
    """
    The VortexManager extends the base (and default) Manager object to provide
    additional methods:
    
    bulk_delete(ids) - a single query, non-chunking delete by id statement
    in_bulk() - extends behavior of in_bulk to return a dictionary of all
                query items when a list of ids is NOT provided, empty lists
                will still return an empty dictionary (as will empty models)
    """
    
    def get_query_set(self):
        """
        """
        return VortexQuerySet(self.model, using=self._db)


    def bulk_delete(self, *args, **kwargs):
        return self.get_query_set().bulk_delete(*args, **kwargs)


    def in_bulk(self, *args, **kwargs):
        return self.get_query_set().in_bulk(*args, **kwargs)
