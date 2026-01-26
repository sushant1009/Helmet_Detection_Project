package com.helmet_detection.helmet_detection_backend.Repository;

import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface WorkersRepository extends JpaRepository<Workers,Long> {
}
