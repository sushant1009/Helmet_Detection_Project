package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.Service.SessionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class WhatsAppWebhookController {

    private final SessionService sessionService;

    public WhatsAppWebhookController(SessionService sessionService) {
        this.sessionService = sessionService;
    }

    @PostMapping("/webhook")
    public ResponseEntity<String> receive(
            @RequestParam("From") String from,
            @RequestParam("Body") String body) {

        String phone = from.replace("whatsapp:", "");
        System.out.println(phone);

        if (body.equalsIgnoreCase("IN")) {
            sessionService.startSession(phone);
        }

        return ResponseEntity.ok("OK");
    }
}
