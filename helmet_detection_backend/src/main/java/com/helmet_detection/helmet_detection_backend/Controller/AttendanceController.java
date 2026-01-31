package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.Entity.Attendance;
import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Service.AttendanceService;
import com.helmet_detection.helmet_detection_backend.Service.SupervisorService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/attendance")
public class AttendanceController {

    private final AttendanceService attendanceService;
    private final SupervisorService supervisorService;

    @PostMapping("/{id}")
    public ResponseEntity<?> markAttendance(@PathVariable Long id, Authentication authentication) {
        try {
            // Get supervisor from authentication email
            String email = authentication.getName();
            Supervisor supervisor = supervisorService.getSupervisorByEmail(email)
                    .orElseThrow(() -> new RuntimeException("Supervisor not found with email: " + email));

            // Call the attendance service to mark attendance
            Attendance attendance = attendanceService.markAttendance(id, supervisor);

            return ResponseEntity.ok(attendance.getAttendanceId());

        } catch (RuntimeException ex) {
            // Return meaningful error response
            Map<String, String> errorResponse = new HashMap<>();
            errorResponse.put("error", ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errorResponse);
        }
    }

}
