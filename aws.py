import os
import boto3


bucket_name = os.getenv("AWS_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")

class AWS:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

    def upload_to_s3(self, file_path, object_name=None):
        if object_name is None:
            object_name = file_path.split("/")[-1]
        
        try:
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            print(f"File '{file_path}' uploaded successfully to '{bucket_name}/{object_name}'.")
        except Exception as e:
            print(f"Error uploading file: {e}")

    def generate_signed_url(self, object_name, expiration=3600):
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            print("Signed URL:", url)
            return url
        except Exception as e:
            print(f"Error generating signed URL: {e}")

    def generate_presigned_url(self, object_name, expiration=3600):
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': object_name,
                    'ResponseContentType': 'video/mp4',  # Ensure it's recognized as a video
                    'ResponseContentDisposition': 'inline'  # Forces streaming instead of downloading
                },
                ExpiresIn=expiration
            )
            print("Signed URL:", url)
            return url
        except Exception as e:
            print(f"Error generating signed URL: {e}")


if __name__ == "__main__":
    aws = AWS()
    # aws.upload_to_s3("/home/mothilal/Downloads/Java For Programmers in 2 hours - Telusko (720p, h264) (1).mp4", "java-video.mp4")
    # aws.generate_signed_url("java-video.mp4")
    aws.generate_presigned_url("java-video.mp4")

