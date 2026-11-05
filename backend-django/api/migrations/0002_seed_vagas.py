from django.db import migrations

VAGAS = [
    ("A01", "CARRO"), ("A02", "CARRO"), ("A03", "CARRO"),
    ("A04", "CARRO"), ("A05", "CARRO"), ("A06", "CARRO"),
    ("A07", "CARRO"), ("A08", "CARRO"), ("A09", "CARRO"),
    ("A10", "CARRO"),
    ("B01", "MOTO"), ("B02", "MOTO"), ("B03", "MOTO"),
    ("B04", "MOTO"), ("B05", "MOTO"),
]


def seed_vagas(apps, schema_editor):
    Vaga = apps.get_model("api", "Vaga")
    Vaga.objects.bulk_create(
        [Vaga(numero=n, tipo=t) for n, t in VAGAS],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [("api", "0001_initial")]
    operations = [migrations.RunPython(seed_vagas, migrations.RunPython.noop)]