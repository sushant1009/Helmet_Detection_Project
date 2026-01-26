package com.helmet_detection.helmet_detection_backend.MongoDB.Repository;

import com.helmet_detection.helmet_detection_backend.MongoDB.Document.EmbeddingsDocument;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EmbeddingsRepository extends MongoRepository<EmbeddingsDocument,String> {
        EmbeddingsDocument findByWorkerId(String workerId);
}
