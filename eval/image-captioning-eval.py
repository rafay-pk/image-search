import csv, numpy as np

ref_captions_fp = "C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/captions.csv"
gen_captions_fp = "C:/Users/Rafay/repos/image-search/eval/matrix.csv"

ref_dict = {}

with open(ref_captions_fp, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        image = row["image"]
        caption = row["caption"]

        if image in ref_dict:
            ref_dict[image].append(caption)
        else:
            ref_dict[image] = [caption]

print("CSV file converted to Python dictionary successfully.")

references = {}
for filename, captions in ref_dict.items():
    temp = []
    for caption in captions:
        caption = caption[:caption.index(' .')] + caption[caption.index('.') + 1:] if ' .' in caption else caption
        temp.append(caption[:1].lower() + caption[1:])
    references[filename] = temp

hypothesis = {}

with open(gen_captions_fp, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        image = row["filename"]
        caption = row["column_name"]

        if image in hypothesis:
            hypothesis[image].append(caption)
        else:
            hypothesis[image] = [caption]

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score

bleu_scores = []
meteor_scores = []
chen_and_cherry = SmoothingFunction()
for file in ref_dict.keys():
    ref = references[file]
    ref = [x.split(' ') for x in ref]
    hyp = hypothesis[file][0]
    hyp = hyp.split(' ')
    if hyp != ['']:
        bleu_scores.append(sentence_bleu(ref, hyp, smoothing_function=chen_and_cherry.method2))
        meteor_scores.append(meteor_score(ref, hyp))

print(f'BLEU: Computed Scores for {len(bleu_scores)} generated captions with a mean score of {np.mean(bleu_scores)}')
print(f'METEOR: Computed Scores for {len(meteor_scores)} generated captions with a mean score of {np.mean(meteor_scores)}')

from pycocoevalcap.cider.cider import Cider
from pycocoevalcap.spice.spice import Spice

hyp = {}
ref = {}
for filename, caption in hypothesis.items():
    if caption != ['']:
        hyp[filename] = caption

for file in hyp.keys():
    ref[file] = references[file]

cider_scorer = Cider()
spice_scorer = Spice()
cider_score, _ = cider_scorer.compute_score(ref, hyp)
spice_score, _ = spice_scorer.compute_score(ref, hyp)
print(f'CIDER: Computed Scores for {len(hyp)} generated captions with a mean score of {cider_score}')
print(f'SPICE: Computed Scores for {len(hyp)} generated captions with a mean score of {spice_score}')
