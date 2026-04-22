package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.DTO.AttendanceResponse;
import com.helmet_detection.helmet_detection_backend.Entity.Attendance;
import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.AttendanceRepository;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.SupervisorRepository;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.WorkersRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@RequiredArgsConstructor
@Service
public class AttendanceService {

    private final AttendanceRepository attendanceRepository;
    private final WorkersRepository workersRepository;
    private final SupervisorRepository supervisorRepository;

    public Attendance markAttendance(Long workerId, Supervisor supervisor) {

        LocalDate today = LocalDate.now();
        LocalDateTime now = LocalDateTime.now();
        Workers worker = workersRepository.findById(workerId)
                .orElseThrow(() -> new RuntimeException("Worker not found with id: " + workerId));

        Optional<Attendance> existing =
                attendanceRepository.findByWorkerAndDate(worker, today);

        if (existing.isPresent()) {
            Attendance attendance = existing.get();
            attendance.setExitTime(now);
            return attendanceRepository.save(attendance);

        }
        Attendance attendance = new Attendance();
        attendance.setWorker(worker);
        attendance.setDate(today);
        attendance.setEntryTime(now);
        attendance.setSupervisor(supervisor);
        return attendanceRepository.save(attendance);
    }

    public List<AttendanceResponse> getAttendanceByDate(String email,LocalDate date){
        Supervisor supervisor = supervisorRepository.findByEmail(email)
                .orElseThrow(()->new RuntimeException("Supervisor does'nt exist with email"+email));

        Long supervisorId = supervisor.getSupervisorId();

       List<Attendance> attendance = attendanceRepository.findBySupervisor_SupervisorIdAndDate(supervisorId,date);

       return  attendance.stream().map((a)->new AttendanceResponse(
               a.getAttendanceId(),
               a.getWorker().getWorkerId(),
               a.getDate(),
               a.getEntryTime(),
               a.getExitTime()
       )).toList();
    }
}

