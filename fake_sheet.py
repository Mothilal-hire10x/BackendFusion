import os
import gspread
import pandas as pd
from faker import Faker
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

class FakeSheet:
    def __init__(self):
        self.fake = Faker()
        Faker.seed(42)
        self.emails = set()
        self.phones = set()
        self.data = []
        self.google_credentials = os.getenv("GOOGLE_CREDENTIALS")
        self.share_email = os.getenv("SHARE_EMAIL")

    def generate_unique_email(self):
        email = self.fake.email()
        while email in self.emails:
            email = self.fake.email()
        self.emails.add(email)
        return email

    def generate_unique_phone(self):
        phone = self.fake.phone_number()
        while phone in self.phones:
            phone = self.fake.phone_number()
        self.phones.add(phone)
        return phone

    def generate_data(self, count=20000):
        for _ in range(count):
            # Generate fake data
            # You can add more fields as needed
            self.data.append([
                self.fake.name(),
                self.generate_unique_email(),
                self.generate_unique_phone(),
                self.fake.url(),
                self.fake.company(),
                self.fake.job()
            ])

    def upload_to_google_sheet(self):
        # Convert data to DataFrame 
        # and upload to Google Sheet
        df = pd.DataFrame(self.data, columns=["name", "email", "phone", "linkedin", "company_name", "designation"])
        
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_file = self.google_credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        
        sheet = client.create("Fake Leads Sheet")
        sheet.share(self.share_email, perm_type="user", role="writer")
        worksheet = sheet.get_worksheet(0)
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        print(f"Data uploaded to {sheet.url}")

if __name__ == "__main__":
    fake_sheet = FakeSheet()
    fake_sheet.generate_data()
    fake_sheet.upload_to_google_sheet()
