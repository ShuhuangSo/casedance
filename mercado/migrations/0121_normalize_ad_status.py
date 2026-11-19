from django.db import migrations

# 广告报表状态值（西/英，含阴阳性形式）-> 统一编码，与views.py中AD_STATUS_MAP保持一致
STATUS_MAP = {
    'activa': 'ACTIVA', 'activo': 'ACTIVA', 'active': 'ACTIVA',
    'pausada': 'PAUSADA', 'pausado': 'PAUSADA', 'paused': 'PAUSADA',
    'finalizada': 'FINALIZADA', 'finalizado': 'FINALIZADA', 'finished': 'FINALIZADA',
    'archivada': 'ARCHIVADA', 'archivado': 'ARCHIVADA', 'archived': 'ARCHIVADA',
    'movido': 'MOVIDO', 'movida': 'MOVIDO', 'moved': 'MOVIDO',
    'deshabilitado': 'DESHABILITADO', 'deshabilitada': 'DESHABILITADO',
    'disabled': 'DESHABILITADO',
}


def normalize_status(apps, schema_editor):
    for model_name in ('AdProductReport', 'AdCampaignReport'):
        Model = apps.get_model('mercado', model_name)
        for obj in Model.objects.all().iterator():
            raw = (obj.status or '').strip()
            new = STATUS_MAP.get(raw.lower(), raw)
            if new != obj.status:
                obj.status = new
                obj.save(update_fields=['status'])


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0120_auto_20261118_1733'),
    ]

    operations = [
        migrations.RunPython(normalize_status, migrations.RunPython.noop),
    ]
