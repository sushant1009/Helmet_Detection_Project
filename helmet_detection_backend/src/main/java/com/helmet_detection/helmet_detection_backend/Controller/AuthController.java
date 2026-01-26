package com.helmet_detection.helmet_detection_backend.Controller;

import com.helmet_detection.helmet_detection_backend.DTO.AuthResponse;
import com.helmet_detection.helmet_detection_backend.DTO.EmbeddingResponse;
import com.helmet_detection.helmet_detection_backend.DTO.LoginRequest;

import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.MongoDB.Document.EmbeddingsDocument;
import com.helmet_detection.helmet_detection_backend.Security.JwtUtil;
import com.helmet_detection.helmet_detection_backend.MongoDB.Service.EmbeddingsService;
import com.helmet_detection.helmet_detection_backend.Service.SupervisorService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.*;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Date;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final SupervisorService supervisorService;
    private final PasswordEncoder encoder;
    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;
    private final EmbeddingsService embeddingsService;


    @PostMapping(value = "/signup", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> saveSupervisor(
            @RequestParam("fullName") String fullName,
            @RequestParam("aadharNo") String aadharNo,
            @RequestParam("siteName") String siteName,
            @RequestParam("dob") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) Date dob,
            @RequestParam("email") String email,
            @RequestParam("phoneNo") String phoneNo,
            @RequestParam("password") String password,
            @RequestParam("file") MultipartFile file
    ) {
        try {
            // 1 Save file
            String uploadDir = "D:/helmet_photos/";
            Files.createDirectories(Paths.get(uploadDir));

            String fileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
            Path filePath = Paths.get(uploadDir + fileName);
            Files.write(filePath, file.getBytes());

            // 2 Create Supervisor object
            Supervisor supervisor = new Supervisor();
            supervisor.setFullName(fullName);
            supervisor.setAadharNo(aadharNo);
            supervisor.setSiteName(siteName);
            supervisor.setDob(dob);
            supervisor.setEmail(email);
            supervisor.setPhoneNo(phoneNo);
            supervisor.setPhotoPath(filePath.toString());
            supervisor.setCreatedAt(new Date());

            // 3 Encode password (if added later)
            supervisor.setPassword(encoder.encode(password));
            Supervisor saved = supervisorService.saveSupervisor(supervisor);

           String id = supervisorService.saveEmbeddings(file,saved.getSupervisorId(),saved.getSupervisorId());

            if(id != null) {
                return ResponseEntity.ok("Supervisor registerd with id " + saved.getSupervisorId());
            }
            return (ResponseEntity<?>) ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error saving supervisor: " + e.getMessage());
        }
    }




    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {


        try {
            authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            request.getEmail(),
                            request.getPassword()
                    )
            );
        } catch (AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body("Invalid Credentials");
        }
        Supervisor supervisor =
                supervisorService.getSupervisorByEmail(request.getEmail())
                        .map(u -> (Supervisor) u)
                                        .orElseThrow(() ->
                                                new RuntimeException("User not found")
                        );


        // 3 Generate JWT
        String token = jwtUtil.generateToken(supervisor);

        // 4 Return token + role
        if(!token.isEmpty()) {
            return ResponseEntity.ok(
                    new AuthResponse(token, supervisor.getRole())
            );
        }
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
    }


}
