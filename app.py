import os

import requests
import io
from PIL import Image
from flask import Flask, render_template, Response,request
import cv2
import psycopg2
import face_recognition
import numpy as np
from flask_cors import CORS

app=Flask(__name__)
CORS(app)

camera = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
krish_image = face_recognition.load_image_file(r"userPhotos\Teoman/Teoman.jpg")
krish_face_encoding = face_recognition.face_encodings(krish_image)[0]

# Load a second sample picture and learn how to recognize it.
bradley_image = face_recognition.load_image_file(r"userPhotos\Samet/Samet.jpg")
bradley_face_encoding = face_recognition.face_encodings(bradley_image)[0]

hakan_image = face_recognition.load_image_file(r"userPhotos\Hakan/Hakan.jpg")
hakan_face_encoding = face_recognition.face_encodings(hakan_image)[0]


# Create arrays of known face encodings and their names
known_face_encodings = [
    krish_face_encoding,
    bradley_face_encoding,
    hakan_face_encoding
]
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
    print(studentPhoto)
    print(takingPhoto)

    while True:
        frame = takingPhoto  # read the camera frame
        success = True
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time

            # Find all the faces and face encodings in the current frame of video
            studentPhotoEncoding = face_recognition.face_encodings(studentPhoto)[0]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(studentPhotoEncoding, face_encoding)
                name = "Unknown"
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(studentPhotoEncoding, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    print(name)
                face_names.append(name)
            

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
@app.route('/video_feed/<id>', methods=['POST', 'GET'])
def video_feed(id):
    print("entered")
    savedPhoto = requests.get('http://localhost:8080/api/student?id='+id)
    takingPhoto = request.files['file']
    # convert image to numpy array
    image = np.array(Image.open(io.BytesIO(savedPhoto.content)))
    #data2= np.array(r.content)
    return Response(gen_frames(image,takingPhoto),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/test', methods=['GET'])
def test():
    return "testt"

if __name__=='__main__':
    app.run(debug=True)
