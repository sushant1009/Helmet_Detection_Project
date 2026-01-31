import numpy as np
import cv2
import insightface
    
class GenerateEmbeddings:
    def __init__(self):
        self.model = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
        self.model.prepare(ctx_id=-1, det_size=(640, 640))
        
    def take_Photo_and_save_Embeddings(self):        

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = self.model.get(frame_rgb)

            for face in faces:
                bbox = face.bbox.astype(int)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                cv2.putText(frame, "Press 'c' to capture", (bbox[0], bbox[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

            cv2.imshow("Face Capture", frame)
            key = cv2.waitKey(1) & 0xFF
            success = False
            if key == ord('c') and len(faces) > 0:  
                face = faces[0]
                emb = face.embedding
                emb = emb / np.linalg.norm(emb)
                success = True
            
            if success:  
                cap.release()
                cv2.destroyAllWindows()
                    
                return emb
        
    def generate_Embeddings_img(self,image):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces
        faces = self.model.get(img_rgb)

        if not faces or len(faces) == 0:
            print("No face detected in the given image.")
            return None

        # Use the first detected face
        face = faces[0]
        emb = face.embedding
        emb = emb / np.linalg.norm(emb)  # Normalize embedding vector

        return emb