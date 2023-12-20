from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Replace the following with your service account key file and the required scopes
SERVICE_ACCOUNT_FILE = 'path/to/service_account.json'
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
    return folder.get('id')

def create_drive_file(name, mime_type, parent_id=None, content=None):
    """Create a file in Google Drive."""
    service = create_drive_service()
    file_metadata = {
        'name': name,
        'mimeType': mime_type,
        'parents': [parent_id] if parent_id else []
    }

    # For documents and spreadsheets with content
    if content and mime_type in ['application/vnd.google-apps.document', 'application/vnd.google-apps.spreadsheet']:
        file = service.files().create(body=file_metadata, fields='id').execute()
        document_id = file.get('id')
        for request in content:
            service.documents().batchUpdate(documentId=document_id, body={'requests': [request]}).execute()
        return document_id
    else:
        file = service.files().create(body=file_metadata).execute()
        return file.get('id')

# Structure to be created in Google Drive
structure = {
    # ... (paste your structure here)
}

def create_drive_structure(structure):
    """Create the specified folder and file structure in Google Drive."""
    for folder_name, files in structure.items():
        folder_id = create_folder(folder_name)
        for file_name, mime_type, content in files:
            create_drive_file(file_name, mime_type, folder_id, content)
        print(f"Created folder '{folder_name}' with files.")

# Example usage
if __name__ == "__main__":
    create_drive_structure(structure)
