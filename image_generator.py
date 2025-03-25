import os
from dotenv import load_dotenv
import replicate

# load_dotenv()
# api_key = os.getenv("REPLICATE_API_TOKEN")

# os.environ["REPLICATE_API_TOKEN"] = api_key

import requests

class ImageGenerator:
    def __init__(self):
        self.replicate_api_key = "xx"
        self.stability_api_key = "xx"

    def generate_replicate_image(self, prompt: str):
        output = replicate.run(
            "black-forest-labs/flux-pro",
            input={"prompt": prompt}
        )
        return output
    
    def generate_stability_image(self, prompt: str):
        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/ultra",
            headers={
                "authorization": f"Bearer {self.stability_api_key}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "webp",
            },
        )

        if response.status_code == 200:
            with open("./ai_image.webp", 'wb') as file:
                file.write(response.content)
        else:
            raise Exception(str(response.json()))
        

image_gen = ImageGenerator()
image_gen.generate_stability_image("walking laptop on the beach")
