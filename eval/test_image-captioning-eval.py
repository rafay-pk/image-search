import numpy as np, os
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image
import nltk
from pycocoevalcap.spice.spice import Spice
from pycocoevalcap.cider.cider import Cider

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


def parse_captions_file(filename):
    captions = dict()
    for line in open(filename).readlines()[1:]:
        parts = line.split(',')
        captions[parts[0]] = parts[1].split('.', 1)[0][0:-1].split(' ')
    return captions


# nltk.download('wordnet')
# nltk.download('wordnet_ic')
# nltk.download('averaged_perceptron_tagger')

# references = parse_captions_file('dataset/flickr8k/captions.txt')
# # scores = np.full(len(references), 0, dtype='float')
# scores = []
# image_path = 'C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/Images'
# smooth_fx = nltk.translate.bleu_score.SmoothingFunction()
# hyp = {}
# ref = {}
# spice_scorer = Spice()
# cider_scorer = Cider()
# file_count = len(os.listdir(image_path))
# for i, file in enumerate(os.listdir(image_path)):
#     caption = predict_step(f'{image_path}/{file}')[0].split(' ')
#     # hyp[f'image{i}'] = predict_step(f'{image_path}/{file}')
#     reference = references[file]
#     # ref[f'image{i}'] = [' '.join(references[file])]
#     scores.append(nltk.translate.bleu_score.sentence_bleu([reference], caption, smoothing_function=smooth_fx.method2))
#     # score = nltk.translate.bleu_score.sentence_bleu([reference], caption)
#     # score = nltk.trameteor_score([reference], caption)
#     # score, _ = spice_scorer.compute_score(ref, hyp)
#     # score, _ = cider_scorer.compute_score(ref, hyp)
#     # scores[i] = score
#     # print(f'Reference Caption:{reference}')
#     # print(f'Generated Caption:{caption}')
#     # print(f'File:{file}, Score:{score}, Overall: {np.mean(scores[np.nonzero(scores)])}')
#     # print(f'File:{file}, Overall: {score}')
#     print(f'Generating Caption {i}/{file_count}')
#
# score = np.mean(scores)
# # score, _ = cider_scorer.compute_score(ref, hyp)
# print(score)
#
#

# ref = 'A big dog in a blue house'
# res = 'A dog in room with blue walls'
# # res = 'tommy doing bad things to hafsa khan'
# smth = SmoothingFunction()
# print(sentence_bleu([ref.split(' ')], res.split(' '), smoothing_function=smth.method2))

path = r'C:\Users\Rafay\OneDrive\data'
for file in os.listdir(path):
    if os.path.isfile(os.path.join(path, file)):
        print(f'Image:{os.path.join(path, file)}, Caption:{predict_step(os.path.join(path, file))}')
# [print(f'Image:{os.path.join(path, file)}, Caption:{predict_step(os.path.join(path, file))}') for file in os.listdir(path) if os.path.isfile(file)]