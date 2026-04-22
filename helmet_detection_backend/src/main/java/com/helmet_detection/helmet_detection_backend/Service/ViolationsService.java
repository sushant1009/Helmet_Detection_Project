package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.DTO.ViolationResponse;
import com.helmet_detection.helmet_detection_backend.Entity.Violations;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.SupervisorRepository;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.ViolationsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ViolationsService {
    private final ViolationsRepository violationsRepository;
    private final SupervisorRepository supervisorRepository;

    public Violations saveVoilation(Violations voilation)
    {
        return violationsRepository.save(voilation);
    }

    public List<ViolationResponse> getVoialations(String email, LocalDate date){
            Long supervisorId = supervisorRepository.findByEmail(email).get().getSupervisorId();
            List<Violations> violations = violationsRepository.findBySupervisor_SupervisorIdAndDate(supervisorId,date);
        return violations.stream().map((v) ->
                new ViolationResponse(v.getWorker().getWorkerId(),
                        v.getWorker().getFullName(),
                        v.getDate(),
                        v.getFilePath(),
                        v.getScore(),
                        v.getSupervisor().getSiteName())).toList();
    }


}
