# Generated by Django 5.0.3 on 2024-03-27 19:33

import django.core.validators
import django.db.models.deletion
import simple_history.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seguimiento', '0002_comentario_tipo_historicalcomentario_tipo_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Origen_Proyecto',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=90, unique=True, verbose_name='Nombre')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
            ],
        ),
        migrations.CreateModel(
            name='PM_Proyecto',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=90, unique=True, verbose_name='Nombre')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
            ],
        ),
        migrations.CreateModel(
            name='Tipo_Proyecto',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=90, unique=True, verbose_name='Nombre')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
            ],
        ),
        migrations.RemoveField(
            model_name='comentario',
            name='proyecto',
        ),
        migrations.AddField(
            model_name='comentario',
            name='obj_id',
            field=models.CharField(blank=True, default='', max_length=36, verbose_name='Objeto'),
        ),
        migrations.AddField(
            model_name='historicalcomentario',
            name='obj_id',
            field=models.CharField(blank=True, default='', max_length=36, verbose_name='Objeto'),
        ),
        migrations.AddField(
            model_name='historicalproyecto',
            name='lider',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Lider'),
        ),
        migrations.AddField(
            model_name='historicalproyecto_tarea',
            name='prioridad',
            field=models.PositiveSmallIntegerField(choices=[(10, 'Baja'), (20, 'Media'), (30, 'Alta')], default=10),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='lider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL, verbose_name='Lider'),
        ),
        migrations.AddField(
            model_name='proyecto_tarea',
            name='prioridad',
            field=models.PositiveSmallIntegerField(choices=[(10, 'Baja'), (20, 'Media'), (30, 'Alta')], default=10),
        ),
        migrations.AlterField(
            model_name='comentario',
            name='creacion',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creación'),
        ),
        migrations.AlterField(
            model_name='historicalproyecto_tarea',
            name='complejidad',
            field=models.PositiveSmallIntegerField(default=1, help_text='Complejidad de 1 a 100', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(1)], verbose_name='Complejidad'),
        ),
        migrations.AlterField(
            model_name='historicalproyecto_tarea',
            name='finalizado',
            field=models.PositiveSmallIntegerField(default=0, help_text='Porcentaje de activdad completada de 0 - 100%', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], verbose_name='% Completado'),
        ),
        migrations.AlterField(
            model_name='proyecto_tarea',
            name='complejidad',
            field=models.PositiveSmallIntegerField(default=1, help_text='Complejidad de 1 a 100', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(1)], verbose_name='Complejidad'),
        ),
        migrations.AlterField(
            model_name='proyecto_tarea',
            name='finalizado',
            field=models.PositiveSmallIntegerField(default=0, help_text='Porcentaje de activdad completada de 0 - 100%', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)], verbose_name='% Completado'),
        ),
        migrations.CreateModel(
            name='HistoricalOrigen_Proyecto',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('nombre', models.CharField(db_index=True, max_length=90, verbose_name='Nombre')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical origen_ proyecto',
                'verbose_name_plural': 'historical origen_ proyectos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPM_Proyecto',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('nombre', models.CharField(db_index=True, max_length=90, verbose_name='Nombre')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical p m_ proyecto',
                'verbose_name_plural': 'historical p m_ proyectos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalTipo_Proyecto',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('nombre', models.CharField(db_index=True, max_length=90, verbose_name='Nombre')),
                ('vigente', models.BooleanField(default=True, verbose_name='Estado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical tipo_ proyecto',
                'verbose_name_plural': 'historical tipo_ proyectos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name='historicalproyecto',
            name='origen',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='seguimiento.origen_proyecto', verbose_name='Origen de proyecto'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='origen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='seguimiento.origen_proyecto', verbose_name='Origen de proyecto'),
        ),
        migrations.AddField(
            model_name='historicalproyecto',
            name='pm',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='seguimiento.pm_proyecto', verbose_name='Project Manager'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='pm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='seguimiento.pm_proyecto', verbose_name='Project Manager'),
        ),
        migrations.AddField(
            model_name='historicalproyecto',
            name='tipo',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='seguimiento.tipo_proyecto', verbose_name='Tipo de proyecto'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='tipo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='seguimiento.tipo_proyecto', verbose_name='Tipo de proyecto'),
        ),
    ]
