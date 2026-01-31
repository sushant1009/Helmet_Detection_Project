package com.helmet_detection.helmet_detection_backend.Repository.Jpa;

import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface WorkersRepository extends JpaRepository<Workers,Long> {

    long countBySupervisorSupervisorId(Long supervisorId);

    Optional<Workers> findByEmail(String email);
    boolean existsByEmail(String email);
    boolean existsByAadharNo(String aadhar);
}
