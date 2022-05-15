import requests
import io
from PIL import Image,ImageDraw
from flask import Flask, Response, request, jsonify, json
import cv2
import face_recognition
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Create arrays of known face encodings and their names

known_face_names = [
    "Teoman",
    "Samet",
    "Hakan"
]
# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

def gen_frames(studentPhoto,takingPhoto):

    frame = takingPhoto  # read the camera frame numpy


    # Only process every other frame of video to save time

    # Find all the faces and face encodings in the current frame of video
    known_face_names = ["Samet Toylan"]
    studentPhotoEncoding = face_recognition.face_encodings(studentPhoto)[0]

    face_locations = face_recognition.face_locations(takingPhoto)
    face_encodings = face_recognition.face_encodings(takingPhoto, face_locations)
    pil_image = Image.fromarray(takingPhoto)
    draw = ImageDraw.Draw(pil_image)
    known_face_encodings = studentPhotoEncoding

    matches = face_recognition.compare_faces(known_face_encodings, face_encodings)
    #Instead, use face_distance to calculate similarities
    face_distances = face_recognition.face_distance(known_face_encodings, face_encodings)
    best_match_index = np.argmin(face_distances)
    name = "Unknown"
    if matches[best_match_index]:
        name = known_face_names[best_match_index]
        print(name)
        return 'true'
    # Draw a box around the face using the Pillow module
    print(name)
    return 'false'

@app.route('/', methods=['POST', 'GET'])
def index():
    return "succesful"
@app.route('/video_feed/<id>', methods=['POST', 'GET'])
def video_feed(id):
    if request.method == "POST":
        savedPhoto = requests.get('https://meta-gen.herokuapp.com/api/student/get-photo?studentId=' + id)
        takingPhoto = request.files['file']
        # convert image to numpy array
        takesPhoto = face_recognition.load_image_file(takingPhoto)
        image = io.BytesIO(savedPhoto.content)
        dbPhoto = face_recognition.load_image_file(image)
        variable = gen_frames(dbPhoto,takesPhoto)
        return app.response_class(response=json.dumps(variable),
                                  status=200,
                                  mimetype='application/json')

if __name__=='__main__':
    app.run(debug=True)
