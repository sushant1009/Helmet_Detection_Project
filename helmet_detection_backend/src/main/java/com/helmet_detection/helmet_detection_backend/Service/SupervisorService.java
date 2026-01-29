package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.DTO.EmbeddingResponse;
import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Repository.SupervisorRepository;
import lombok.RequiredArgsConstructor;
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

import java.io.IOException;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class SupervisorService {
    private final SupervisorRepository supervisorRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    public Supervisor saveSupervisor(Supervisor supervisor){
        return supervisorRepository.save(supervisor);
    }

    public Optional<Supervisor> getSupervisorByEmail(String email) {
        return supervisorRepository.findByEmail(email);
    }

    public String saveEmbeddings(MultipartFile file, Long workerId, Long supervisorId) throws IOException {

        String url = "http://localhost:8001/get-embeddings";

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
        body.add("workerId",workerId);
        body.add("supervisorId",supervisorId);

        HttpEntity<MultiValueMap<String, Object>> requestEntity =
                new HttpEntity<>(body, headers);

        ResponseEntity<EmbeddingResponse> response =
                restTemplate.postForEntity(url, requestEntity, EmbeddingResponse.class);

        return response.getBody().getId();
    }

    public boolean existEmail(String email) {
        return supervisorRepository.existsByEmail(email);
    }


}
