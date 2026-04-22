package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.DTO.AttendanceResponse;
import com.helmet_detection.helmet_detection_backend.DTO.WorkersDTO;
import com.helmet_detection.helmet_detection_backend.Entity.Attendance;
import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import com.helmet_detection.helmet_detection_backend.MongoDB.Service.EmbeddingsService;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.SupervisorRepository;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.WorkersRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class WorkerService {
    private final WorkersRepository workersRepository;
    private final EmbeddingsService embeddingsService;
    private final SupervisorRepository supervisorRepository;

    public Workers registerWorker(Workers worker) {
        return workersRepository.save(worker);
    }


    public void deleteWorker(Long id) {
        workersRepository.deleteById(id);
    }
    @Transactional
    public Workers registerWorkerWithEmbeddings(MultipartFile file, Workers worker) throws Exception {
        Workers saved = workersRepository.save(worker);

        String id = embeddingsService.saveEmbeddings(file, saved.getWorkerId(),
                saved.getSupervisor().getSupervisorId());

        if (id == null) {
            throw new RuntimeException("Embedding failed");
        }

        return saved;
    }

    public List<WorkersDTO> getRegisteredWorkers(String email){
        Supervisor supervisor = supervisorRepository.findByEmail(email)
                .orElseThrow(()->new RuntimeException("Supervisor does'nt exist with email"+email));

        Long supervisorId = supervisor.getSupervisorId();

        List<Workers> workers = workersRepository.findBySupervisorSupervisorId(supervisorId);

        return  workers.stream().map((w)->new WorkersDTO(
               w.getWorkerId(),
                w.getFullName(),
                w.getAadharNo(),
                w.getEmail(),
                w.getDob(),
                w.getPhoneNo(),
                w.getStatus(),
                w.getSupervisor().getSupervisorId(),
                w.getPhotoPath()
        )).toList();
    }



    public Optional<Workers> findByEmail(String email) {
        return workersRepository.findByEmail(email);
    }

    public Optional<Workers> getByWorkerId(Long workerId){
        return workersRepository.findById(workerId);
    }

    public boolean existsByEmail(String email){
       return workersRepository.existsByEmail(email);
    }
    public boolean existsByAadharNo(String aadhar){
        return workersRepository.existsByAadharNo(aadhar);
    }


}