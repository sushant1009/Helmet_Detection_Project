package com.helmet_detection.helmet_detection_backend.DTO;

import lombok.Data;

import java.util.List;

@Data
public class EmbeddingResponse {
    private List<Double> embedding;
}
