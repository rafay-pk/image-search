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

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds


# dataset generation
# dataset_images = 'C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/Images/'
# dataset_captions = 'C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/captions.csv'

# csv_filename = "C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/captions.csv"  # Replace with the actual filename
csv_filename = "dataset/flickr8k/captions.csv"  # Replace with the actual filename

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

# Create matrix CSV file with unique filenames and an empty column
# folder_path = "C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/Images/"
folder_path = "dataset/flickr8k/Images/"
matrix_filename = "matrix.csv"

unique_filenames = set(captions_dict.keys())

if not os.path.exists(matrix_filename):
    with open(matrix_filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "column_name"])  # Header row

        for filename in unique_filenames:
            # file_path = os.path.join(folder_path, filename)
            writer.writerow([filename, ""])

    print(f"Matrix file '{matrix_filename}' has been created.")

length = len(os.listdir(folder_path))
# Iterate over the matrix and update the column
with open(matrix_filename, "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)  # Read all rows into a list

for i, row in enumerate(rows):
    filename = row["filename"]
    column_name = row["column_name"]

    # Check if the column is empty
    if not column_name:
        # Perform operations on the filename
        # Example: Process the image, extract features, etc.
        print(f'Processing {i+2}/{length}')
        # Update the column with a value indicating completion
        row["column_name"] = predict_step(os.path.join(folder_path, filename))[0]

        # Write the updated matrix back to the CSV file
        with open(matrix_filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["filename", "column_name"])
            writer.writeheader()
            writer.writerows(rows)

print("Iteration over the matrix is complete.")

# matrix = np.array([line.split('|') for line in open(dataset_captions)])
# matrix[:, 1] = np.char.rstrip(matrix[:, 1], '\n')
# matrix = np.hstack([matrix, np.empty((matrix.shape[0],1), dtype=str)])
# matrix = [row for row in matrix if os.path.exists(f'{dataset_images}{row[0]}')]
#
# pd.DataFrame(matrix).to_csv('dataset/flickr8k/captions.csv', header=None, index=None)

# path = 'C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/captions.csv'
# csv = np.genfromtxt(path, delimiter=',', dtype='U', invalid_raise=False, usecols=(0, 1, 2))
# length = csv.shape[0]
# for i, row in enumerate(csv):
#     if row[2] != '':
#         continue
#     print(f'Generating Caption for File:{i}/{length} with Ref:{row[1]}')
#     row[2] = predict_step(f'{dataset_images}{row[0]}')[0]
#     pd.DataFrame(csv).to_csv('dataset/flickr8k/captions.csv', header=None, index=None)
#
# # print(predict_step([r"C:\Users\Rafay\data\New folder 2\35b83a082e4b7e36c6b696bb1feea61b.gif"]))
