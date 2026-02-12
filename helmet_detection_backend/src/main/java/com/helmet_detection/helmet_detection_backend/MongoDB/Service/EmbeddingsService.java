package com.helmet_detection.helmet_detection_backend.MongoDB.Service;

import com.helmet_detection.helmet_detection_backend.DTO.EmbeddingResponse;
import com.helmet_detection.helmet_detection_backend.MongoDB.Document.EmbeddingsDocument;
import com.helmet_detection.helmet_detection_backend.Repository.Mongo.EmbeddingsRepository;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Value;

import java.io.IOException;

@Service
public class EmbeddingsService {
    private final EmbeddingsRepository embeddingsRepository;
    private final RestTemplate restTemplate;


     @Value("${embeddings.server.url}")
    private String url;

    public EmbeddingsService(EmbeddingsRepository embeddingsRepository, RestTemplate restTemplate) {
        this.embeddingsRepository = embeddingsRepository;
        this.restTemplate = restTemplate;
    }

    public String saveEmbeddings(MultipartFile file, Long workerId, Long supervisorId) throws IOException {



        // Headers
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        // Body
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }

        });


        HttpEntity<MultiValueMap<String, Object>> requestEntity =
                new HttpEntity<>(body, headers);

        ResponseEntity<EmbeddingResponse> response =
                restTemplate.postForEntity(url, requestEntity, EmbeddingResponse.class);
        EmbeddingsDocument embeddingsDocument = new EmbeddingsDocument();
        System.out.println("Response "+response);
        embeddingsDocument.setEmbeddings(response.getBody().getEmbedding());
        embeddingsDocument.setWorkerId(workerId);
        embeddingsDocument.setSupervisorId(supervisorId);
       embeddingsDocument = embeddingsRepository.save(embeddingsDocument);
        return embeddingsDocument.getId() ;
    }

    public EmbeddingsDocument getEmbeddingsByworkerId(Long workerId)
    {
        return embeddingsRepository.findByWorkerId(workerId);
    }

}
