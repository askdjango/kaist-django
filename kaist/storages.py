from storages.backends.azure_storage import AzureStorage
from storages.utils import setting

class StaticAzureStorage(AzureStorage):
    azure_container = setting("AZURE_CONTAINER")

class MediaAzureStorage(AzureStorage):
    azure_container = setting("AZURE_MEDIA_CONTAINER")
