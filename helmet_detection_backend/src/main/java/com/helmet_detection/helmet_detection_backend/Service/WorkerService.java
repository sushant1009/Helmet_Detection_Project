package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import com.helmet_detection.helmet_detection_backend.Repository.WorkersRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class WorkerService {
    private final WorkersRepository workersRepository;

    public Workers registerWorker(Workers worker) {
        return workersRepository.save(worker);
    }

    public void deleteWorker(Long id) {
        workersRepository.deleteById(id);
    }


    public Optional<Workers> findByEmail(String email) {
        return workersRepository.findByEmail(email);
    }

    public Optional<Workers> getByWorkerId(Long workerId){
        return workersRepository.findById(workerId);
    }
}