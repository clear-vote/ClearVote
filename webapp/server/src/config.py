from google.cloud import secretmanager
import os

def access_secret_version(project_id, secret_id, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')

class Config:
    PROJECT_ID = "clear-vote-app"
    SECRET_KEY = access_secret_version(PROJECT_ID, "SECRET_KEY")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")