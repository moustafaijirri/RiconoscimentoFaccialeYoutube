import face_recognition, cv2, os, glob, sys, tempfile
from pytube import YouTube


def extractFileName(fullPathFile):
    return os.path.splitext(os.path.basename(fullPathFile))[0]

def encodeFaceFile(fullPathFile):
    loadedFile = face_recognition.load_image_file(fullPathFile)
    return face_recognition.face_encodings(loadedFile)[0]

def playAndRecognitionOfFaces(videoFullPath, dirImageFaces):
    face_files = [f for f in glob.glob(dirImageFaces+'/*')]
    print("Face Files: " + str(face_files))

    known_face_names = [extractFileName(f) for f in face_files]
    known_face_encodings = [encodeFaceFile(f) for f in face_files]

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    video_capture = cv2.VideoCapture(videoFullPath)

    while video_capture.isOpened():

        ret, frame = video_capture.read()

        if ret :
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]


            if process_this_frame:

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:

                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Nada"

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]

                    face_names.append(name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):

                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


            cv2.imshow('Video [Premi q per uscire]', frame)

        # q per uscire
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_capture.release()
            cv2.destroyAllWindows()
            break

def downloadFromYouTube(urlTube):
    print("Downloading video: " + urlTube)
    yt = YouTube(urlTube)
    yt.streams.first().download()
    random_file_name = tempfile.NamedTemporaryFile(prefix="youtube-movie-", dir=".").name
    os.rename(yt.streams.first().default_filename, random_file_name)
    print("Scaricato come: " + random_file_name)
    return random_file_name

def main():
    if len(sys.argv) < 2:
        print("Utilizzo :")
        print("python recfacial.py https://www.youtube.com/watch?v=DjOXpbpPU-U faces/")
        exit(-1)
    else:
        dir_faces  = sys.argv[2]
        youtube_url = sys.argv[1]
        movie_file = downloadFromYouTube(youtube_url)
        playAndRecognitionOfFaces(movie_file, dir_faces)


if __name__ == "__main__":
    main()