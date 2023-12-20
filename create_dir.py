from google.oauth2 import service_account
from googleapiclient.discovery import build

# Replace the following with your service account key file and the required scopes
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']


def create_drive_service():
    """Create a Google Drive service instance."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    return service


def create_folder(name, parent_id=None):
    """Create a folder in Google Drive."""
    service = create_drive_service()
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]

    folder = service.files().create(body=file_metadata, fields='id').execute()
    print(f"Folder '{name}' created with ID: {folder.get('id')}")

    # Example usage
    # if __name__ == "__main__":
create_folder("test_20231220")
