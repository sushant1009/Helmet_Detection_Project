package com.helmet_detection.helmet_detection_backend.DTO;

import lombok.Data;

@Data
public class LoginRequest {
    private String email;
    private String password;
}