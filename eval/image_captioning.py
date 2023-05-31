from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch, os, csv
from PIL import Image


model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}


def predict_step(path):
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert(mode="RGB")

    pixel_values = feature_extractor(images=[img], return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    output_ids = model.generate(pixel_values, **gen_kwargs)

    predictions = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    predictions = [pred.strip() for pred in predictions]
    return predictions


csv_filename = "dataset/flickr8k/captions.csv"

captions_dict = {}

with open(csv_filename, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        image = row["image"]
        caption = row["caption"]

        if image in captions_dict:
            captions_dict[image].append(caption)
        else:
            captions_dict[image] = [caption]

print("CSV file converted to Python dictionary successfully.")

folder_path = "dataset/flickr8k/Images/"
matrix_filename = "matrix.csv"

unique_filenames = set(captions_dict.keys())

if not os.path.exists(matrix_filename):
    with open(matrix_filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "column_name"])  # Header row

        for filename in unique_filenames:
            writer.writerow([filename, ""])

    print(f"Matrix file '{matrix_filename}' has been created.")

length = len(os.listdir(folder_path))
with open(matrix_filename, "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)  # Read all rows into a list

for i, row in enumerate(rows):
    filename = row["filename"]
    column_name = row["column_name"]

    if not column_name:
        print(f'Processing {i+2}/{length}')
        row["column_name"] = predict_step(os.path.join(folder_path, filename))[0]

        with open(matrix_filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["filename", "column_name"])
            writer.writeheader()
            writer.writerows(rows)

print("Iteration over the matrix is complete.")