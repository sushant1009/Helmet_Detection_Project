package com.helmet_detection.helmet_detection_backend.DTO;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.RequiredArgsConstructor;

import java.time.LocalDate;

@Data
@AllArgsConstructor
public class ViolationResponse {

    private Long workerId;
    private String workerName;
    private LocalDate date;
    private String filePath;
    private Float score;
    private String siteName;

}
