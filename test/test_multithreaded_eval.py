import torch, os
from PIL import Image
from multiprocessing import Process, Semaphore
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from pycocoevalcap.cider.cider import Cider

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

# execute a task
def task(i, file, hypothesi, referenci, shared_semaphore):
    # acquire the semaphore
    with shared_semaphore:
        hypothesi[f'image{i}'] = predict_step(f'{image_path}/{file}')
        referenci[f'image{i}'] = [' '.join(references[file])]
        print(f'Generating Caption {i}/{file_count}')


# protect the entry point
if __name__ == '__main__':
    model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    max_length = 16
    num_beams = 4
    gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

    references = parse_captions_file('C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/captions.txt')
    image_path = 'C:/Users/Rafay/repos/image-search/eval/dataset/flickr8k/Images'
    hyp = {}
    ref = {}
    cider_scorer = Cider()
    file_count = len(os.listdir(image_path))

    semaphore = Semaphore(5)
    # create all tasks
    processes = [Process(target=task, args=(i,file, *hyp, *ref,semaphore)) for i, file in enumerate(os.listdir(image_path))]
    # start all processes
    for process in processes:
        process.start()
    # wait for all processes to complete
    for process in processes:
        process.join()
    # report that all tasks are completed
    print('Done', flush=True)
