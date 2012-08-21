# -*- coding: utf-8 -*
from __future__ import print_function
from collections import defaultdict, Counter

from django.db import transaction

from castle.utilities.console import ask_boolean, display_counter


def bulk_update(Cls, new_items, key_attrs, value_attr, filters=None, non_property_filters=None, dry_run=False, comparator=lambda a, b: a == b, prompt=False):
    """
    * Cls: the django model class
    * new_items: The items to be checked against the database, stored in a
        python dictionary of key(s): value
    * value_attr: String representing the name of the Metric's value attribute
    * filters: consistent properties of both the new and old items that will be
        added to newly created items.
    * non_property_filters: consistent properties of both the new and old items
        that will NOT be added to newly created items.
    
    * prompt: prompt the user before changes are made

    Employs a consistent cache and Django 1.4's bulk operations.
    
    !!! WARNING !!!
    This updater makes the assumption that the new_items are UNIQUE, which
    means duplicated items or combinations of insert+delete will result in
    undefined behavior.
    """
    # TODO inherit another transaction?
    # TODO Allow single (non-iterator) keys and key_attrs?
    
    # Assert that this object supports bulk creates and deletes
    # Only vortex-managed models have bulk_delete
    assert hasattr(Cls.objects, 'bulk_create'), "Class {class_name} does not have a bulk create method".format(class_name=Cls._meta)
    assert hasattr(Cls.objects, 'bulk_delete'), "Class {class_name} does not have a bulk delete method".format(class_name=Cls._meta)
    
    if not filters:
        filters = {}
    if not non_property_filters:
        non_property_filters = {}
    
    # See if the model object has a comparator
    if hasattr(Cls, "comparator"):
        # The model comparator should accept two values and return a boolean
        comparator = getattr(Cls, "comparator")

    # Build a cache object - TODO could be rolled into a dict comprehension
    cache = {}
    for obj in Cls.objects.filter(**filters).filter(**non_property_filters):
        cache[tuple([getattr(obj, key_attr) for key_attr in key_attrs])] = obj
    
    # Status indicator - count of what happens to each of the new items
    # added / deleted / updated / value_unchanged / ignored_zero
    # NOTE: not a count of final operations
    status = Counter()

    inserts = [] # (key, object to be created)
    updates = [] # (key, object to be updated)
    deletes = [] # (key, id to delete)
     
    with transaction.commit_on_success():
        for key, value in new_items.items():
            if key in cache:
                old = cache[key]
                if value and comparator(getattr(old, value_attr), value):
                    status['value_unchanged'] += 1
                    pass
                elif value:
                    # Value is different
                    setattr(old, value_attr, value)
                    updates.append((key, old))
                    status['updated'] += 1
                else:
                    # Value is now zero, delete the existing entry
                    deletes.append((key, old.id))
                    del cache[key]
                    status['deleted'] += 1
            else:
                # TODO make value check optional?
                if value:
                    props = dict(zip(key_attrs, key))
                    props[value_attr] = value
                    props.update(filters)
                    new_obj = Cls(**props)
                    cache[key] = new_obj
                    inserts.append((key, new_obj))
                    status['added'] += 1
                else:
                    # Zero values are no saved to the database
                    status['ignored_zero'] += 1
    
        if not dry_run:
            if prompt:
                # Output the counter object
                display_counter(status)
                if ask_boolean("Do you wish to continue?"):
                    bulk_commit(Cls, updates, inserts, deletes)
            else:
                bulk_commit(Cls, updates, inserts, deletes)

    return status


def bulk_commit(Cls, updates, inserts, deletes):
    """
    Bulk database operations for updates and inserts.
    """
    # TODO chunk these operations?

    # Add both the updates and deletes to the set of ids to be deleted
    delete_ids = set()
    for key, obj in updates:
        delete_ids.add(obj.id)
    
    for key, obj_id in deletes:
        delete_ids.add(obj_id)
    
    # TODO any safety? check for duplicates? confirm state with the cache?
    
    # Perform the bulk delete
    Cls.objects.bulk_delete(delete_ids)
    
    # TODO currently, the inserts that have pks are run in a separate sql
    # command, if they were located at the front of the list, would there be
    # no chance of collision with auto-increment of the NULL pk inserts?
    
    # Bulk create the pseudo-updates. Since these already have a primary key,
    # they must be created before any new objects are inserted (potentially
    # stealing their primary key)
    update_objs = [obj for key, obj in updates]
    Cls.objects.bulk_create(update_objs)
    
    # Bulk create new inserts
    create_objs = [obj for key, obj in inserts]
    Cls.objects.bulk_create(create_objs)
