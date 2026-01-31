package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.SupervisorRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class SupervisorService {
    private final SupervisorRepository supervisorRepository;


    public Supervisor saveSupervisor(Supervisor supervisor){
        return supervisorRepository.save(supervisor);
    }

    public Optional<Supervisor> getSupervisorByEmail(String email) {
        return supervisorRepository.findByEmail(email);
    }


    public boolean existEmail(String email) {
        return supervisorRepository.existsByEmail(email);
    }


}
