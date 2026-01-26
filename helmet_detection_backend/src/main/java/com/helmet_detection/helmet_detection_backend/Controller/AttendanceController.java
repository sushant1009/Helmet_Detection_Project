package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.Service.AttendanceService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/attendance")
public class AttendanceController {

    private final AttendanceService attendanceService;

    @GetMapping("{id}")
    public void markAttendance(@RequestParam Long id){
        attendanceService.markAttendance(id);
    }
}
