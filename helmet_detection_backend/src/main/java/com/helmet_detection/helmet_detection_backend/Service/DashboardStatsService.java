package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.DTO.DashboardStats;
import com.helmet_detection.helmet_detection_backend.Repository.AttendanceRepository;
import com.helmet_detection.helmet_detection_backend.Repository.ViolationsRepository;
import com.helmet_detection.helmet_detection_backend.Repository.WorkersRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class DashboardStatsService {

    private final WorkersRepository workerRepository;
    private final AttendanceRepository attendanceRepository;
    private final ViolationsRepository violationsRepository;

    public DashboardStats getDashboardStats(Long supervisorId) {
        long workers = workerRepository.countBySupervisorSupervisorId(supervisorId);
        long attendance = attendanceRepository
                .countBySupervisorSupervisorIdAndDate(supervisorId, LocalDate.now());
        long violations = violationsRepository
                .countBySupervisorSupervisorIdAndDate(supervisorId, LocalDate.now());

        return new DashboardStats(workers, attendance, violations);
    }
}
