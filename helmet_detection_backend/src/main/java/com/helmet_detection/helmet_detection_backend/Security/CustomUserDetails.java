package com.helmet_detection.helmet_detection_backend.Security;

import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import com.helmet_detection.helmet_detection_backend.Repository.Jpa.SupervisorRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.Collection;

@RequiredArgsConstructor
public class CustomUserDetails implements UserDetails {

    private Long supervisorId;
    private String email;
    private String password;
    private Collection<? extends GrantedAuthority> authorities;


    public Long getSupervisorId() {
        return supervisorId;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return authorities;
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public String getUsername() {
        return email;
    }

    @Override
    public boolean isAccountNonExpired() { return true; }

    @Override
    public boolean isAccountNonLocked() { return true; }

    @Override
    public boolean isCredentialsNonExpired() { return true; }

    @Override
    public boolean isEnabled() { return true; }

    @Service
    @RequiredArgsConstructor
    public static class CustomUserDetailsService implements UserDetailsService {

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
}

