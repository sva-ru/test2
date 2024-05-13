import yaml
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from netology_pd_diplom.celery import app
from backend.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter, Import_file, \
    ConfirmEmailToken, User

@app.task()
def do_import(file_id, user):
    try:
        file = Import_file.objects.get(id=file_id)
        # print(file.yaml_file.name)
        with open(file.yaml_file.name) as fh:
            # Load YAML data from the file
            data = yaml.load(fh, Loader=yaml.SafeLoader)

        shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=user)
        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()
        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for item in data['goods']:
            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
            product_info = ProductInfo.objects.create(product_id=product.id,
                                                      external_id=item['id'],
                                                      model=item['model'],
                                                      price=item['price'],
                                                      price_rrc=item['price_rrc'],
                                                      quantity=item['quantity'],
                                                      shop_id=shop.id)
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(product_info_id=product_info.id,
                                                parameter_id=parameter_object.id,
                                                value=value)
        Import_file.objects.filter(id=file_id).update(status="Success")
        return "Success"
    except:
        Import_file.objects.filter(id=file_id).update(status="Error")
        return "Error"


@app.task
def send_token_to_email(user_id, title,  **kwargs):
    """
    Отправляем письмо с токеном пользователю
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"{title}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()


@app.task
def send_mail_user(user_id, title, message, **kwargs):
    """
    Отправляем письмо пользователю
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"{title}",
        # message:
        f"{message}",
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()









