package com.helmet_detection.helmet_detection_backend.DTO;

import lombok.Data;

@Data
public class VoilationRequest {
    private Long workerId;
    private Float score;
}
