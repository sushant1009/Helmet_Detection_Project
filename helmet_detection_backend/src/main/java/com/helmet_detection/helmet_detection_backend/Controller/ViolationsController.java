package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.DTO.VoilationRequest;
import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Entity.Violations;
import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import com.helmet_detection.helmet_detection_backend.Service.EmailService;
import com.helmet_detection.helmet_detection_backend.Service.SupervisorService;
import com.helmet_detection.helmet_detection_backend.Service.ViolationsService;
import com.helmet_detection.helmet_detection_backend.Service.WorkerService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.Optional;

@RestController
@RequestMapping("/api/worker/voilations")
@RequiredArgsConstructor
public class ViolationsController {

    private final WorkerService workerService;
    private final ViolationsService violationsService;
    private final SupervisorService supervisorService;
    private final EmailService emailService;

    @PostMapping("/")
    public ResponseEntity<?> saveVoilation(
            @RequestBody VoilationRequest voilationRequest,
            Authentication authentication) {


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

String body = "Helmet violation detected.\n worker Id : "+voilationRequest.getWorkerId()+"\nConfidence: "+voilationRequest.getScore()+"\nViolation duration exceeded 5 minutes.\nKindly wear Safety Helmet to avoid any Accidents...\n\t!!! Thank You !!!" ;

String subject = "Safety Helmet Violation Alert";

emailService.sendEmail(workerOpt.get().getEmail(), subject, body);

        return ResponseEntity.status(HttpStatus.CREATED)
                .body(voilation.getVoilationId());
    }
}
