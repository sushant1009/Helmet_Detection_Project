package com.helmet_detection.helmet_detection_backend.DTO;

import java.time.LocalDateTime;

public class OtpData {

    private final String otp;
    private final LocalDateTime expiryTime;

    public OtpData(String otp, LocalDateTime expiryTime) {
        this.otp = otp;
        this.expiryTime = expiryTime;
    }

    public String getOtp() {
        return otp;
    }

    public LocalDateTime getExpiryTime() {
        return expiryTime;
    }
}

