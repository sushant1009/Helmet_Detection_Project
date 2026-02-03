import numpy as np
import cv2
import insightface
    
class GenerateEmbeddings:
    def __init__(self):
        self.model = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
        self.model.prepare(ctx_id=-1, det_size=(640, 640))
        
        
    def generate_embeddings_img(self,image):
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