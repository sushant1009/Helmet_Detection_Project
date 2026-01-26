package com.helmet_detection.helmet_detection_backend.MongoDB.Service;

import com.helmet_detection.helmet_detection_backend.MongoDB.Document.EmbeddingsDocument;
import com.helmet_detection.helmet_detection_backend.MongoDB.Repository.EmbeddingsRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class EmbeddingsService {
    private final EmbeddingsRepository embeddingsRepository;

    public EmbeddingsDocument saveEmbeddings(EmbeddingsDocument embeddings)
    {
        return embeddingsRepository.save(embeddings);
    }

}
