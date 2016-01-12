# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.db import models, migrations


def forwards(apps, schema_editor):
    change_foreign_keys(apps, schema_editor,
                        "auth", "User",
                        "accounts", "User")


def backwards(apps, schema_editor):
    change_foreign_keys(apps, schema_editor,
                        "accounts", "User",
                        "auth", "User")


def change_foreign_keys(apps, schema_editor, from_app, from_model_name, to_app, to_model_name):
    FromModel = apps.get_model(from_app, from_model_name)
    ToModel = apps.get_model(to_app, to_model_name)

    # We don't make assumptions about which model is being pointed to by
    # AUTH_USER_MODEL. So include fields from both FromModel and ToModel.
    # Only one of them will actually have FK fields pointing to them.

    import sys
    if sys.version_info >= (3,):
        from warnings import warn
        warn("This migration seems to only work on Py2, as of Django 1.9")

    print()
    fields = FromModel._meta.get_fields(include_hidden=True) + ToModel._meta.get_fields(include_hidden=True)

    for rel in fields:
        if not hasattr(rel, 'field') or not isinstance(rel.field, models.ForeignKey):
            continue
        fk_field = rel.field

        f_name, f_field_name, pos_args, kw_args = fk_field.deconstruct()

        # fk_field might have been the old or new one. We need to fix things up.
        old_field_kwargs = kw_args.copy()
        old_field_kwargs['to'] = FromModel
        old_field = fk_field.__class__(*pos_args, **old_field_kwargs)
        old_field.model = fk_field.model

        new_field_kwargs = kw_args.copy()
        new_field_kwargs['to'] = ToModel
        new_field = fk_field.__class__(*pos_args, **new_field_kwargs)
        new_field.model = fk_field.model

        if fk_field.model._meta.auto_created:
            # If this is a FK that is part of an M2M on the model itself,
            # we've already dealt with this, by virtue of the data migration
            # that populates the auto-created M2M field.
            if fk_field.model._meta.auto_created in [ToModel, FromModel]:
                print("Skipping {0}".format(repr(rel)))
                continue

            # In this case (FK fields that are part of an autogenerated M2M),
            # the column name in the new M2M might be different to that in the
            # old M2M. This makes things much harder, and involves duplicating
            # some Django logic.

            # Build a correct ForeignKey field, as it should
            # have been on FromModel
            old_field.name = from_model_name.lower()
            old_field.column = "{0}_id".format(old_field.name)

            # build a correct ForeignKey field, as it should
            # be on ToModel
            new_field.name = to_model_name.lower()
            new_field.column = "{0}_id".format(new_field.name)
        else:
            old_field.name = fk_field.name
            old_field.column = fk_field.column
            new_field.name = fk_field.name
            new_field.column = fk_field.column

        show = lambda m: "{0}.{1}".format(m._meta.app_label, m.__name__)
#        print("Fixing FK in {0}, col {1} -> {2}, from {3} -> {4}".format(
#            show(fk_field.model),
#            old_field.column, new_field.column,
#            show(old_field.remote_field.to), show(new_field.remote_field.to),
#        ))

        schema_editor.alter_field(fk_field.model, old_field, new_field, strict=True)



class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_populate_migration'),
        ('admin', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
        ('course', '0080_auto_20160112_1254'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
