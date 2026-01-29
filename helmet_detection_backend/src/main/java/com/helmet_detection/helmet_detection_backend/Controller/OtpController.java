package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Service.OtpService;
import com.helmet_detection.helmet_detection_backend.Service.SupervisorService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class OtpController {

    private final OtpService otpService;
    private final SupervisorService supervisorService;
    private final PasswordEncoder passwordEncoder;
    private final Set<String> verifiedEmails = ConcurrentHashMap.newKeySet();


    // Send OTP
    @PostMapping("/send-otp/pass")
    public ResponseEntity<String> sendOtpforPassChanege(@RequestParam String email) {
        if(supervisorService.existEmail(email) )
        {
            otpService.sendOtpforPassChanege(email);
            return ResponseEntity.ok("OTP sent successfully");
        }
       return ResponseEntity.status(HttpStatus.NOT_FOUND).body("User Not Found");
    }

    // Send OTP
    @PostMapping("/send-otp")
    public ResponseEntity<String> sendOtp(@RequestParam String email) {
            otpService.sendOtp(email);
            return ResponseEntity.ok("OTP sent successfully");
    }

    // Verify OTP
    @PostMapping("/verify-otp")
    public ResponseEntity<String> verifyOtp(
            @RequestParam String email,
            @RequestParam String otp) {

        boolean verified = otpService.verifyOtp(email, otp);

        if (verified) {
            verifiedEmails.add(email);
            return ResponseEntity.ok("OTP verified successfully");
        } else {
            return ResponseEntity.badRequest().body("Invalid or expired OTP");
        }
    }

    @PutMapping("/change-pass")
    public ResponseEntity<?> changePassword(@RequestParam String email,
                                            @RequestParam String newPassword) {

        if (!verifiedEmails.contains(email)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body("OTP verification required");
        }
        if(supervisorService.existEmail(email)) {
            Supervisor supervisor = supervisorService.getSupervisorByEmail(email)
                    .orElseThrow(() -> new RuntimeException("User not found"));

            supervisor.setPassword(passwordEncoder.encode(newPassword));
            supervisorService.saveSupervisor(supervisor);

            verifiedEmails.remove(email);

            return ResponseEntity.ok("Password changed successfully");
        }
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("User not found with provided email");
    }
}

