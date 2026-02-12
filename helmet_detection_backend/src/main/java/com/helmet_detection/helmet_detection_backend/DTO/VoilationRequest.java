package com.helmet_detection.helmet_detection_backend.DTO;

import lombok.Data;

import java.io.File;

@Data
public class VoilationRequest {
    private Long workerId;
    private Float score;
    private File image;
}
