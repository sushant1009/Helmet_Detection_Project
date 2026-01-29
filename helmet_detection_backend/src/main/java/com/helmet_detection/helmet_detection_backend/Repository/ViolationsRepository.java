package com.helmet_detection.helmet_detection_backend.Repository;

import com.helmet_detection.helmet_detection_backend.Entity.Violations;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;

public interface ViolationsRepository extends JpaRepository<Violations,Long> {
    long countBySupervisorSupervisorIdAndDate(Long supervisorId, LocalDate date);
}
