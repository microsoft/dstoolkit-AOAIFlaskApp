import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# keyVaultName = os.environ["KEY_VAULT_NAME"]
keyVaultName = "" #TODO: Make this an environment variable
KVUri = f"https://{keyVaultName}.vault.azure.net"

default_credential = DefaultAzureCredential()

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

secretName = "OPENAIAPIKEY"

print(f"Retrieving your secret from {keyVaultName}.")

retrieved_secret = client.get_secret(secretName)

print(f"Your secret is '{retrieved_secret.value}'.")