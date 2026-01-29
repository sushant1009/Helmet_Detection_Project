package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.DTO.OtpData;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class OtpService {

    private final EmailService emailService;

    // email -> otp data
    private final Map<String, OtpData> otpStore = new ConcurrentHashMap<>();

    private static final int OTP_EXPIRY_MINUTES = 5;

    public OtpService(EmailService emailService) {
        this.emailService = emailService;
    }

    // Generate 6-digit OTP
    private String generateOtp() {
        return String.valueOf(100000 + new Random().nextInt(900000));
    }

    // Send OTP
    public void sendOtp(String email) {
        String otp = generateOtp();
        LocalDateTime expiry = LocalDateTime.now().plusMinutes(OTP_EXPIRY_MINUTES);

        otpStore.put(email, new OtpData(otp, expiry));

        String subject = "SearchOff | Worker Registration";
        String body =
                "Your OTP is: " + otp + "\n\n" +
                        "This OTP is valid for 5 minutes.\n" +
                        "Do not share this OTP with anyone.";

        emailService.sendEmail(email, subject, body);
    }

    // Verify OTP
    public boolean verifyOtp(String email, String otp) {
        OtpData otpData = otpStore.get(email);

        if (otpData == null) {
            return false;
        }

        if (otpData.getExpiryTime().isBefore(LocalDateTime.now())) {
            otpStore.remove(email);
            return false;
        }

        boolean valid = otpData.getOtp().equals(otp);


        if (valid) {
            otpStore.remove(email);
        }

        return valid;
    }


    public void sendOtpforPassChanege(String email) {
        String otp = generateOtp();
        LocalDateTime expiry = LocalDateTime.now().plusMinutes(OTP_EXPIRY_MINUTES);

        otpStore.put(email, new OtpData(otp, expiry));

        String subject = "SearchOff | Reset Password";
        String body =
                "Your OTP is: " + otp + "\n\n" +
                        "This OTP is valid for 5 minutes.\n" +
                        "Do not share this OTP with anyone.";

        emailService.sendEmail(email, subject, body);
    }
}
