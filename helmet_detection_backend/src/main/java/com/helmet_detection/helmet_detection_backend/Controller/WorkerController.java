package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Entity.Workers;
import com.helmet_detection.helmet_detection_backend.Entity.WorkersStatus;
import com.helmet_detection.helmet_detection_backend.MongoDB.Document.EmbeddingsDocument;
import com.helmet_detection.helmet_detection_backend.MongoDB.Service.EmbeddingsService;
import com.helmet_detection.helmet_detection_backend.Service.SupervisorService;
import com.helmet_detection.helmet_detection_backend.Service.WorkerService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Date;

@RestController
@RequestMapping("/api/worker")
@RequiredArgsConstructor
public class WorkerController {


    private final SupervisorService supervisorService;
    private final WorkerService workerService;
    private final EmbeddingsService embeddingsService;

    @PostMapping(value = "/register", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> registerWorker(Authentication authentication,
            @RequestParam("fullName") String fullName,
                                            @RequestParam("aadharNo") String aadharNo,
                                            @RequestParam("dob") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) Date dob,
                                            @RequestParam("email") String email,
                                            @RequestParam("phoneNo") String phoneNo,
                                            @RequestParam("file") MultipartFile file
    ) {
        String Semail = authentication.getName();
        System.out.println(Semail);
        try {
            // 1 Save file
            String uploadDir = "D:/helmet_photos/";
            Files.createDirectories(Paths.get(uploadDir));

            String fileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
            Path filePath = Paths.get(uploadDir + fileName);
            Files.write(filePath, file.getBytes());

            if(workerService.existsByAadharNo(aadharNo))
            {
                return ResponseEntity.status(HttpStatus.CONFLICT).body("Aadhar Already Exists");
            }
            if(workerService.existsByEmail(email))
            {
                return ResponseEntity.status(HttpStatus.CONFLICT).body("Email Already Exists");
            }

            // 2 Create Supervisor object
            Workers worker = new Workers();
            worker.setFullName(fullName);
            worker.setAadharNo(aadharNo);
            worker.setDob(dob);
            worker.setEmail(email);
            worker.setPhoneNo(phoneNo);
            worker.setPhotoPath(filePath.toString());
            worker.setCreatedAt(new Date());
            worker.setStatus(WorkersStatus.Active);
            Supervisor supervisor = supervisorService.getSupervisorByEmail(Semail).orElse(null);
            if (supervisor != null) {
                worker.setSupervisor(supervisor);
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Invalid Supervisor");
            }

            Workers saved = workerService.registerWorkerWithEmbeddings(file, worker);
            if (saved.getWorkerId() != null)
                return ResponseEntity.ok("Worker registerd with id " + saved.getWorkerId());


        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Embeddings Server Not Available ");
        }
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Error while  saving supervisor: ");
    }

    @GetMapping("/embeddings/{workerId}")
    public EmbeddingsDocument getEmbeddingsByWorkerId(@PathVariable Long workerId)
    {
        System.out.println(workerId);
       return embeddingsService.getEmbeddingsByworkerId(workerId);
    }

}
