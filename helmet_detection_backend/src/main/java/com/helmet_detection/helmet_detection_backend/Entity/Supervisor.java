package com.helmet_detection.helmet_detection_backend.Entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.Date;
import java.util.List;

@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Supervisor {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long supervisorId;

    @Column(nullable = false)
    private String fullName;

    @Column(unique = true)
    private String aadharNo;

    @Column(unique = true)
    private String email;

    @Column(nullable = false)
    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
    private String password;

    @Column(nullable = false)
    private Date dob;

    @Column(nullable = false)
    private String phoneNo;

    @Column(nullable = false)
    private String siteName;

    @Column(nullable = false)
    private String photoPath;

    @Column(nullable = false)
    private Date createdAt;

    @OneToMany(mappedBy = "supervisor")
    @JsonIgnore
    private List<Workers> workers;

    public String getRole(){
        return "SUPERVISOR";
    }
}
