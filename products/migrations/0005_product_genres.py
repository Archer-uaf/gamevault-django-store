from django.db import migrations, models


def copy_primary_category_to_genres(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    through_model = Product._meta.get_field("genres").remote_field.through
    relations = [
        through_model(
            product_id=product.pk,
            category_id=product.category_id,
        )
        for product in Product.objects.iterator()
    ]
    through_model.objects.bulk_create(relations, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0004_product_product_price_positive_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="genres",
            field=models.ManyToManyField(
                blank=True,
                related_name="products_by_genre",
                to="products.category",
            ),
        ),
        migrations.RunPython(
            copy_primary_category_to_genres,
            migrations.RunPython.noop,
        ),
    ]
