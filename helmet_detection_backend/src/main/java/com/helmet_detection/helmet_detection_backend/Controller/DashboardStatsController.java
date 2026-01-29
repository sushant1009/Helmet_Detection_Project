package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Security.CustomUserDetails;
import com.helmet_detection.helmet_detection_backend.Service.DashboardStatsService;
import com.helmet_detection.helmet_detection_backend.Service.SupervisorService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/dashboard")
public class DashboardStatsController {

    private final SupervisorService supervisorService;
    private final DashboardStatsService dashboardStatsService;

    @GetMapping("/stats")
   public ResponseEntity<?> getDashboardStats(Authentication authentication){
        String email = authentication.getName();

        Supervisor supervisor = supervisorService
                .getSupervisorByEmail(email)
                .orElseThrow(() -> new RuntimeException("Supervisor not found"));

        return ResponseEntity.ok(
                dashboardStatsService.getDashboardStats(supervisor.getSupervisorId())
        );
    }
}
