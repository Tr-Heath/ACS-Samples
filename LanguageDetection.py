from dotenv import load_dotenv
import os
import http.client, base64, json, urllib
from urllib import request, parse, error
from azure.keyvault.secrets import SecretClient
from azure.identity import AzureCliCredential

def main():
    global cog_endpoint
    global cog_key

    try:
        #Get configuration settings
        cog_endpoint = os.getenv('COG_SERVICE_ENDPOINT')
        cog_keyname = os.getenv('COG_SERVICE_KEYNAME')

        print(cog_endpoint)

        #get actual key value out of Azure Key Vault
        keyVaultName = os.environ["KEY_VAULT_NAME"]
        keyVaultURI = f"https://{keyVaultName}.vault.azure.net"
        credential = AzureCliCredential()
        client = SecretClient(vault_url=keyVaultURI, credential=credential)
        cog_key = client.get_secret(cog_keyname)

        print(f"KeyVaultName: {keyVaultName}")
        print(f"KeyName: {cog_keyname}")
        print(f"KeyValue: {cog_key}")

        userText = ""
        #Get repeated user input until user exit flag
        while userText.lower() != "quit":
            userText = input("What shall we parse? ")
            GetLanguage(userText)

    except Exception as ex:
        print(ex)

def GetLanguage(userText):
    try:
        #collection of documents with an id and text value
        requestBody = {
            "documents": [
                {"id": 1,
                "text": userText}
            ]
        }

        print(json.dumps(requestBody, indent=2))

        uri = cog_endpoint.rstrip('/').replace('https://', '')
        conn = http.client.HTTPSConnection(uri)
        print("connection made")

        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': cog_key
        }

        print(str(requestBody).encode("utf-8"))
        

        conn.request("POST", "/text/analytics/v3.0/languages?", str(requestBody).encode("utf-8"), headers)
        response = conn.getresponse()
        print("got response")
        data = response.read().decode("utf-8")
        print("got data")

        if response.status == 200:
            results = json.loads(data)

            print(json.dumps(requestBody, indent=2))
            for document in results["documents"]:
                print("\nLanguage: ", document["detectedLanguage"]["name"])
        #else we did not get 200 and have an error, print the data we did get if anything
        else: 
            print(data)

        conn.close()
    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()