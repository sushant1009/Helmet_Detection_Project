package com.helmet_detection.helmet_detection_backend.DTO;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class AttendanceResponse {

    private Long attendanceId;
    private Long workerId;
    private LocalDate date;
    private LocalDateTime entryTime;
    private LocalDateTime exitTime;

}
