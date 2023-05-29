from pycocoevalcap.cider.cider import Cider


hyp = {
    "image1": ["This is a cat."],
    "image2": ["A dog is running."]
}

# References
ref = {
    "image1": ["This is a cat.", "A cat is sitting."],
    "image2": ["A dog is running.", "The dog runs fast."]
}


cider_scorer = Cider()
score, _ = cider_scorer.compute_score(ref, hyp)

print(score)
# print(scores)