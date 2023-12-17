from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import googleapiclient.errors

from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents',
          'https://www.googleapis.com/auth/spreadsheets']


class VacationPlanner:
    def __init__(self, service_account_file, user_email):
        self.service_account_file = service_account_file
        self.user_email = user_email
        self.service = self.authenticate('drive', 'v3')
        self.docs_service = self.authenticate('docs', 'v1')
        self.sheets_service = self.authenticate('sheets', 'v4')

    def authenticate(self, api, version):
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=SCOPES)
        delegated_credentials = credentials.with_subject(self.user_email)
        return build(api, version, credentials=delegated_credentials)

    def create_directory(self, name, parent_id=None):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        print(f"Directory created: {name} (ID: {file.get('id')})")
        return file.get('id')

    def create_file(self, name, mime_type, parent_id, content=None):
        file_metadata = {
            'name': name,
            'mimeType': mime_type,
            'parents': [parent_id]
        }
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        file_id = file.get('id')

        if content:
            if mime_type == 'application/vnd.google-apps.document':
                self.populate_google_doc(file_id, content)
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                self.populate_google_sheet(file_id, content)

        print(f"File created: {name} (ID: {file_id})")
        return file_id

    def populate_google_doc(self, document_id, content):
        try:
            self.docs_service.documents().batchUpdate(documentId=document_id, body={'requests': content}).execute()
        except googleapiclient.errors.HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def populate_google_sheet(self, spreadsheet_id, content):
        try:
            self.sheets_service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'valueInputOption': 'USER_ENTERED', 'data': content}
            ).execute()
        except googleapiclient.errors.HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def setup_vacation_planning_structure(self):
        root_id = self.create_directory('VacationPlanning2023')

        # Define the structure and initial content for each file
        structure = {
            '01_DestinationIdeas': [
                ('LongList_Destinations.docx', 'application/vnd.google-apps.document', [
                    {'insertText': {'location': {'index': 1},
                                    'text': 'European Beach Destination Ideas:\n\n1. Santorini, Greece\n2. Ibiza, Spain\n3. French Riviera, France\n4. Amalfi Coast, Italy\n5. Algarve, Portugal\n\nAdd more destinations that interest you...'}}
                ]),
                ('ShortList_Destinations.docx', 'application/vnd.google-apps.document', [
                    {'insertText': {'location': {'index': 1},
                                    'text': 'Shortlisted European Beach Destinations:\n\nDiscuss and finalize your top choices here...'}}
                ])
            ],
            '02_TimeOffRequests': [
                ('PublicServiceEmployee_Request.docx', 'application/vnd.google-apps.document', [
                    {'insertText': {'location': {'index': 1},
                                    'text': 'Time Off Request - Guidelines\n\n[Include specific request procedures for public service employee here...]'}}
                ]),
                ('OtherMembers_Request.docx', 'application/vnd.google-apps.document', [
                    {'insertText': {'location': {'index': 1},
                                    'text': 'Time Off Request - Guidelines\n\n[Include general request procedures for other members here...]'}}
                ])
            ],
            '03_BudgetPlanning': [
                ('OverallBudget.xlsx', 'application/vnd.google-apps.spreadsheet', None),  # Add a template for budgeting
                ('PersonalContributions.xlsx', 'application/vnd.google-apps.spreadsheet', None)
                # Add a template for tracking personal contributions
            ],
            '04_Accommodations': [
                ('HotelOptions.docx', 'application/vnd.google-apps.document', []),
                ('AirbnbOptions.docx', 'application/vnd.google-apps.document', [])
            ],
            '05_Transportation': [
                ('FlightOptions.xlsx', 'application/vnd.google-apps.spreadsheet', None),
                ('LocalTransportation.docx', 'application/vnd.google-apps.document', [])
            ],
            '06_Activities': [
                ('ActivitiesList.docx', 'application/vnd.google-apps.document', [
                    {'insertText': {'location': {'index': 1},
                                    'text': "Possible Activities:\n\n1. Beach Volleyball\n2. Scuba Diving\n3. Yacht Tour\n4. Local Cuisine Tasting\n\nAdd more activities you're interested in..."}}
                ]),
                ('BookedActivities.xlsx', 'application/vnd.google-apps.spreadsheet', None)
            ],
            '07_EmergencyContacts': [
                ('LocalEmergencyNumbers.docx', 'application/vnd.google-apps.document', []),
                ('ContactsBackHome.docx', 'application/vnd.google-apps.document', [])
            ]
        }

        for dir_name, files in structure.items():
            dir_id = self.create_directory(dir_name, root_id)
            for file_name, mime_type, content in files:
                self.create_file(file_name, mime_type, dir_id, content)


# Usage
planner = VacationPlanner('service_account.json', 'kilian@familylehn.com')
planner.setup_vacation_planning_structure()
