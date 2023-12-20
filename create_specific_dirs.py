from google.oauth2 import service_account
from googleapiclient.discovery import build

# Replace the following with your service account key file and the required scopes
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']


def create_drive_service(user_email):
    """Create a Google Drive service instance with domain-wide delegation."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(user_email)
    service = build('drive', 'v3', credentials=delegated_credentials)
    return service


def create_folder(name, parent_id=None, user_email='admin@example.com'):
    """Create a folder in Google Drive."""
    service = create_drive_service(user_email)
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]

    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')


def share_folder_with_user(folder_id, user_email, user_email_to_share):
    """Share the specified folder with a user."""
    service = create_drive_service(user_email)
    user_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': user_email_to_share
    }
    service.permissions().create(
        fileId=folder_id,
        body=user_permission,
        fields='id'
    ).execute()


def create_drive_structure(folder_names, admin_email, share_with_email):
    """Create folders in Google Drive and share them."""
    for folder_name in folder_names:
        folder_id = create_folder(folder_name, user_email=admin_email)
        share_folder_with_user(folder_id, admin_email, share_with_email)
        print(f"Created and shared folder '{folder_name}'.")


# Example usage
folder_names = ['Folder1', 'Folder2', 'Folder3']  # Replace with your list of folder names

# Example usage
admin_email = 'kilian@familylehn.com'  # Replace with your admin email
share_with_email = 'kilian@familylehn.com'  # User to share folders with

if __name__ == "__main__":
    create_drive_structure(folder_names, admin_email, share_with_email)
