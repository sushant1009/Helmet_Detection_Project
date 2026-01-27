package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.Entity.Attendance;
import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import com.helmet_detection.helmet_detection_backend.Repository.AttendanceRepository;
import com.helmet_detection.helmet_detection_backend.Repository.WorkersRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Optional;

@RequiredArgsConstructor
@Service
public class AttendanceService {

    private final AttendanceRepository attendanceRepository;
    private final WorkersRepository workersRepository;

    public ResponseEntity<?> markAttendance(Long workerId) {

        Workers worker = workersRepository.findById(workerId)
                .orElseThrow(null);

        if(worker == null)
            return  ResponseEntity.status(HttpStatus.NOT_FOUND).body("User Not Found");

        LocalDate today = LocalDate.now();
        LocalDateTime now = LocalDateTime.now();

        Optional<Attendance> existing =
                attendanceRepository.findByWorkerAndDate(worker, today);

        if (existing.isPresent()) {
            Attendance attendance = existing.get();
            attendance.setExitTime(now);
            attendanceRepository.save(attendance);

        } else {
            Attendance attendance = new Attendance();
            attendance.setWorker(worker);
            attendance.setDate(today);
            attendance.setEntryTime(now);
            attendanceRepository.save(attendance);
        }
        return  ResponseEntity.status(HttpStatus.OK).build();
    }
}

