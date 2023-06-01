from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch, os, csv
from PIL import Image

class ImageCaptioner:
    def __init__(self) -> None:
        self.initialized = False

    def initialize(self):
        self.model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        self.feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        self.tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        max_length = 16
        num_beams = 4
        self.gen_kwargs = {"max_length": max_length, "num_beams": num_beams}
    
    def predict_step(self, path):
        if not self.initialized:
            self.initialize()
            self.initialized = True
        img = Image.open(path)
        if img.mode != "RGB":
            img = img.convert(mode="RGB")

        pixel_values = self.feature_extractor(images=[img], return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self.device)

        output_ids = self.model.generate(pixel_values, **self.gen_kwargs)

        predictions = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        return [pred.strip() for pred in predictions]