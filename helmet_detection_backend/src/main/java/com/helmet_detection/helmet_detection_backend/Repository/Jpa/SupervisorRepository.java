package com.helmet_detection.helmet_detection_backend.Repository.Jpa;

import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface SupervisorRepository extends JpaRepository<Supervisor,Long> {
    @Override
    Optional<Supervisor> findById(Long supervisorId);
    Optional<Supervisor> findByEmail(String email);


    boolean existsByEmail(String email);
}
