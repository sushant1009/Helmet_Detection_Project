package com.helmet_detection.helmet_detection_backend.Repository;

import com.helmet_detection.helmet_detection_backend.Entity.Attendance;
import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.Optional;

@Repository
public interface AttendanceRepository extends JpaRepository<Attendance, Long> {
    Optional<Attendance> findByWorkerAndDate(Workers worker, LocalDate date);

    long countBySupervisorSupervisorIdAndDate(Long supervisorId, LocalDate date);
}
