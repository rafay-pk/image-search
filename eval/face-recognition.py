import os, face_recognition, numpy as np, random, dlib, cv2
from PIL import Image

path = r'C:\Users\Rafay\John Wick ScreenGrabs'
upscaled = 'temp.png'
detector = dlib.get_frontal_face_detector()

file_tags = {}
unique_people = {}
faces_detected = 0

for file in os.listdir(path):
    print(f'Processing File:{file}')
    file_tags[file] = []
    full_path = os.path.join(path, file)
    # image = Image.open(full_path)
    # temp = image.resize(tuple(int(x * 1.5) for x in image.size),resample= Image.LANCZOS)
    # temp.save(upscaled)
    # print(detector(cv2.imread(full_path)))
    # image = face_recognition.load_image_file(upscaled)
    image = face_recognition.load_image_file(full_path)
    locations = face_recognition.face_locations(image, 1, model='hog')
    encodings = face_recognition.face_encodings(image, locations, num_jitters=1, model='small')
    if len(encodings) > 0:
        for encoding in encodings:
            faces_detected += 1
            print('Detected Person')
            unique = list(unique_people.values())
            result = face_recognition.compare_faces(unique, encoding)
            check = np.count_nonzero(result)
            if check == 0:
                name = f'person_{random.randint(10000, 99999)}'
                unique_people[name] = encoding
                print('Added New Person')
            elif check == 1:
                name = list(unique_people.keys())[result.index(True)]
            elif check > 1:
                distances = face_recognition.face_distance(unique, encoding)
                name = list(unique_people.keys())[np.argmin(distances)]
            file_tags[file].append(name)

log_file = 'face-recog.txt'
log = open(log_file, "w")

for file_tag in file_tags.items():
    log.write(f'{file_tag[0]}:{", ".join(file_tag[1])}\n')

log.close()
print(f'Detcted {faces_detected} faces and {len(unique_people)} poeple')