package com.helmet_detection.helmet_detection_backend.Service;

import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Repository.SupervisorRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

    private final SupervisorRepository supervisorRepository;

    @Override
    public UserDetails loadUserByUsername(String email)
            throws UsernameNotFoundException {
        Supervisor supervisor = supervisorRepository.findByEmail(email)
                .orElseThrow(() ->
                        new UsernameNotFoundException("User not found: " + email));

        return org.springframework.security.core.userdetails.User
                .withUsername(supervisor.getEmail())
                .password(supervisor.getPassword())
                .roles(supervisor.getRole())
                .build();
    }
}
