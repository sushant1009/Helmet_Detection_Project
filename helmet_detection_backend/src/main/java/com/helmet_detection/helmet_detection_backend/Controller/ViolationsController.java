package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.DTO.VoilationRequest;
import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Entity.Violations;
import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import com.helmet_detection.helmet_detection_backend.Service.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.Date;
import java.util.Optional;

@RestController
@RequestMapping("/api/worker/violations")
@RequiredArgsConstructor
public class ViolationsController {

    private final WorkerService workerService;
    private final ViolationsService violationsService;
    private final SupervisorService supervisorService;
    private final EmailService emailService;
    private final ImageService imageService;

    private final SessionService sessionService;
    private final WhatsAppService whatsAppService;


    @PostMapping("/")
    public ResponseEntity<?> saveVoilation(
            @RequestBody VoilationRequest voilationRequest,
            Authentication authentication) throws IOException {

        Optional<Supervisor> supervisorOpt =
                supervisorService.getSupervisorByEmail(authentication.getName());

        Optional<Workers> workerOpt =
                workerService.getByWorkerId(voilationRequest.getWorkerId());

        if (workerOpt.isEmpty() || supervisorOpt.isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("Worker or Supervisor doesn't exist");
        }

        Violations voilation = new Violations();
        voilation.setWorker(workerOpt.get());
        voilation.setSupervisor(supervisorOpt.get());
        voilation.setScore(voilationRequest.getScore());
        voilation.setDate(LocalDate.now());
        voilation.setTime(LocalDateTime.now());

        voilation = violationsService.saveVoilation(voilation);

        String base64Image = voilationRequest.getImage();

// If it ever contains "data:image/jpeg;base64,"
        if (base64Image.contains(",")) {
            base64Image = base64Image.split(",")[1];
        }

// Decode Base64 → real image bytes
        byte[] imageBytes = Base64.getDecoder().decode(base64Image);

        String phone = "+91"+workerOpt.get().getPhoneNo();

        String link = imageService.uploadViolationImage(imageBytes, String.valueOf(voilation.getVoilationId()),voilation.getDate());
        voilation.setFilePath(link);
        violationsService.saveVoilation(voilation);
        if (sessionService.isActive(phone)) {

            whatsAppService.sendAlert(
                    phone,
                    "🚨 Helmet violation detected.\n worker Id : "+voilationRequest.getWorkerId()+"\nConfidence:"+voilationRequest.getScore()+"\nViolation duration exceeded 5 minutes.\nKindly wear Safety Helmet to avoid any Accidents...\n\t!!! Thank You !!!\n Captured Image:- "
            );


        }


        return ResponseEntity.status(HttpStatus.CREATED)
                .body(voilation.getVoilationId());
    }


    @PostMapping("/supervisor/")
    public ResponseEntity<?> alertSupervisor(
            @RequestBody VoilationRequest voilationRequest,
            Authentication authentication) throws IOException {

        Optional<Supervisor> supervisorOpt =
                supervisorService.getSupervisorByEmail(authentication.getName());

        Optional<Workers> workerOpt =
                workerService.getByWorkerId(voilationRequest.getWorkerId());

        if (workerOpt.isEmpty() || supervisorOpt.isEmpty()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("Worker or Supervisor doesn't exist");
        }

        Violations voilation = new Violations();
        voilation.setWorker(workerOpt.get());
        voilation.setSupervisor(supervisorOpt.get());
        voilation.setScore(voilationRequest.getScore());
        voilation.setDate(LocalDate.now());
        voilation.setTime(LocalDateTime.now());

        voilation = violationsService.saveVoilation(voilation);

        String base64Image = voilationRequest.getImage();

// If it ever contains "data:image/jpeg;base64,"
        if (base64Image.contains(",")) {
            base64Image = base64Image.split(",")[1];
        }

// Decode Base64 → real image bytes
        byte[] imageBytes = Base64.getDecoder().decode(base64Image);

        String phone = "+91"+supervisorOpt.get().getPhoneNo();

        String link = imageService.uploadViolationImage(imageBytes, String.valueOf(voilation.getVoilationId()),voilation.getDate());
        voilation.setFilePath(link);
        violationsService.saveVoilation(voilation);
        System.out.println(phone);
        if (sessionService.isActive(phone)) {

            whatsAppService.sendAlert(
                    phone,
                    "🚨 Helmet violation detected.\n worker Id : "+voilationRequest.getWorkerId()+"\nConfidence: "+voilationRequest.getScore()+"\nViolation duration exceeded 10 minutes.\nKindly inform him to wear Safety Helmet to avoid any Accidents...\n\t!!! Thank You !!!\n Captured Image:- "
            );


        }


        return ResponseEntity.status(HttpStatus.CREATED)
                .body(voilation.getVoilationId());
    }





}
