from datetime import timedelta
from google.cloud import storage

import os
from dotenv import load_dotenv

load_dotenv()
bucket_name = os.getenv("BUCKET_NAME")
google_credentials = os.getenv("GOOGLE_CREDENTIALS")


class GCP:
    def __init__(self):
        self.storage_client = storage.Client.from_service_account_json(google_credentials)
        self.bucket = self.storage_client.bucket(bucket_name)

    def upload_to_gcs(self, source_file_path: str, destination_blob_name: str) -> None:
        """Uploads a file to Google Cloud Storage."""
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)
        print(f"File {source_file_path} uploaded to {self.bucket.name}/{destination_blob_name}.")

    def generate_signed_url(self, blob_name: str) -> str:
        """Generates a signed URL for a blob."""
        blob = self.bucket.blob(blob_name)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=24),
            method="GET",
        )
        return url

    def delete_blob(self, blob_name: str) -> None:
        """Deletes a blob from the bucket."""
        blob = self.bucket.blob(blob_name)
        blob.delete()
        print(f"Blob {blob_name} deleted.")

    def delete_all_blobs(self) -> None:
        """Deletes all blobs in the bucket."""
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            blob.delete()
        print(f"All blobs in {self.bucket.name} deleted.")

    def list_blobs(self) -> None:
        """Lists all blobs in the bucket."""
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            print(blob.name)

    def download_blob(self, blob_name: str) -> None:
        """Downloads a blob to a local file."""
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(blob_name)

    def download_all_blobs(self) -> None:
        """Downloads all blobs in the bucket to local files."""
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            blob.download_to_filename(blob.name)

    def list_blobs_with_prefix(self, prefix: str) -> None:
        """Lists all blobs in the bucket with a given prefix."""
        blobs = self.bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            print(blob.name)

    def get_blob_details(self, blob_name: str) -> None:
        """Gets the details of a blob."""
        blob = self.bucket.blob(blob_name)
        blob.reload()  # Ensures metadata is loaded

        if blob.exists():
            print(f"Blob Name: {blob.name}")
            print(f"Size: {blob.size} bytes")
            print(f"Content Type: {blob.content_type}")
        else:
            print(f"Blob '{blob_name}' does not exist.")



if __name__ == "__main__":
    gcp = GCP()
    # gcp.upload_to_gcs("/home/mothilal/Downloads/Java For Programmers in 2 hours - Telusko (720p, h264) (1).mp4", "courses/java-video.mp4")
    print(gcp.generate_signed_url("courses/java-video.mp4"))
    # gcp.delete_blob("video.mp4")
    # gcp.get_blob_details("courses/333/modules/592/materials/Learn React Router with a Beginners Project  Learn React JS - Dave Gray (720p, h264).mp4")
    # gcp.download_blob("video.mp4")
    # gcp.download_all_blobs()
    # gcp.list_blobs()
    # gcp.list_blobs_with_prefix("video")
