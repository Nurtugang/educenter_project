import os
from dotenv import load_dotenv
from amocrm.v2 import tokens, Pipeline, Lead, Contact as _Contact, custom_field, fields

load_dotenv()

client_id = os.getenv('AMOCRM_CLIENT_ID')
client_secret = os.getenv('AMOCRM_CLIENT_SECRET')
subdomain = os.getenv('AMOCRM_SUBDOMAIN')
redirect_url = os.getenv('AMOCRM_REDIRECT_URL')
long_token = os.getenv('LONG_TOKEN')
token2029 = os.getenv('LONGLONG_TOKEN')

tokens.default_token_manager(
    client_id=client_id,
    client_secret=client_secret,
    subdomain=subdomain,
    redirect_url=redirect_url,
    storage=tokens.FileTokensStorage(),  # можно изменить на другой способ хранения
)

# Проверка инициализации токена
def init_amocrm_tokens():
    try:
        # Инициализация токена, используя сохранённый код авторизации
        tokens.default_token_manager.init(code=token2029, skip_error=True)
    except Exception as e:
        print(f"Ошибка инициализации токена: {e}")

init_amocrm_tokens()

class Contact(_Contact):
    name = fields._Field("name")
    phone_number = custom_field.TextAreaCustomField("phone_number")


def create_contact(contact_name, phone_number):
    new_contact = Contact()
    new_contact.name = contact_name
    new_contact.phone_number = phone_number
    new_contact.save()  # Сохраняем контакт в amoCRM

    return new_contact


def get_pipeline_id():
    pipelines = Pipeline.objects.all()
    for pipeline in pipelines:
        if pipeline.name == "senim-school.com":
            lead_pipeline_id = pipeline.id
            break
    
    return lead_pipeline_id

def create_lead(pipeline_id, contact):
    lead_name = "Первичный контакт - senim-school.com"
    new_lead = Lead()
    new_lead.name = lead_name
    new_lead.pipeline = pipeline_id
    new_lead.save()
    
    contact.leads.add(new_lead)
    if new_lead.id:
        contact.leads.add(new_lead)
        return True
    else:
        return False

