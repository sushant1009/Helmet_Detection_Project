package com.helmet_detection.helmet_detection_backend.Service;

import com.twilio.rest.api.v2010.account.Message;
import com.twilio.type.PhoneNumber;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class WhatsAppService {

    @Value("${twilio.whatsapp.from}")
    private String from;

    public void sendAlert(String to, String messageText) {

        Message message = Message.creator(
                new PhoneNumber("whatsapp:" + to),
                new PhoneNumber(from),
                messageText
        ).create();

        System.out.println("Message SID: " + message.getSid());
    }


}
