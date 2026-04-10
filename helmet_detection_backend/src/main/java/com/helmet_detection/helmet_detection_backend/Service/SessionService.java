package com.helmet_detection.helmet_detection_backend.Service;

import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@Service
public class SessionService {

    private Map<String, LocalDateTime> sessions = new HashMap<>();

    public void startSession(String phone) {
        sessions.put(phone, LocalDateTime.now());
    }

    public boolean isActive(String phone) {
        LocalDateTime last = sessions.get(phone);

        return last != null &&
                Duration.between(last, LocalDateTime.now()).toHours() < 24;
    }
}
