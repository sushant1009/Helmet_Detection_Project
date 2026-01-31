package com.helmet_detection.helmet_detection_backend.MongoDB.Document;


import com.fasterxml.jackson.annotation.JsonIgnore;
import org.springframework.data.annotation.Id;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.Date;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "embeddings")
public class EmbeddingsDocument {
    @Id
    private String id;
    private Long workerId;
    private Long supervisorId;
    private List<Double> embeddings;
    @JsonIgnore
    private Date createdAt =  new Date();
}
