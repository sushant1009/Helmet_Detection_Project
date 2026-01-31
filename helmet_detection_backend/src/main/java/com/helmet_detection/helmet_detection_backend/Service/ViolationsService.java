package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.Entity.Violations;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.ViolationsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ViolationsService {
    private final ViolationsRepository violationsRepository;

    public Violations saveVoilation(Violations voilation)
    {
        return violationsRepository.save(voilation);
    }

}
