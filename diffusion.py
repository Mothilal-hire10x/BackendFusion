from diffusers import DiffusionPipeline
import torch

# Load Kandinsky prior (text-to-image embeddings)
prior = DiffusionPipeline.from_pretrained("kandinsky-community/kandinsky-2-2-prior", torch_dtype=torch.float32)
prior.to("cpu")  # Use CPU (change to "cuda" if you have a GPU)

# Generate image embeddings from text prompt
prompt = "A scenic mountain view with a river flowing through it"
negative_prompt = "blurry, low quality, bad lighting"  # Optional: Negative prompt for guidance
generator = torch.manual_seed(0)  # Fix randomness for reproducibility

# 🔹 Get both image and negative embeddings
prior_output = prior(prompt=prompt, negative_prompt=negative_prompt, generator=generator)
image_embeds = prior_output.image_embeds
negative_image_embeds = prior_output.negative_image_embeds  # FIXED!

# Load Kandinsky decoder (convert embeddings to image)
decoder = DiffusionPipeline.from_pretrained("kandinsky-community/kandinsky-2-2-decoder", torch_dtype=torch.float32)
decoder.to("cpu")  # Use CPU (change to "cuda" if you have a GPU)

# Generate final image from embeddings
image = decoder(image_embeds=image_embeds, negative_image_embeds=negative_image_embeds).images[0]
image.save("kandinsky_output.png")

print("Image saved as kandinsky_output.png")
