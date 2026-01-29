package com.helmet_detection.helmet_detection_backend.Entity;


import jakarta.persistence.*;
import lombok.*;

import java.util.Date;

@Entity
@Data
@AllArgsConstructor
@NoArgsConstructor
@Setter
public class Workers {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long workerId;

    @Column(nullable = false)
    private String fullName;

    @Column(unique = true)
    private String aadharNo;

    @Column(unique = true)
    private String email;

    @Column(nullable = false)
    private Date dob;

    @Column(nullable = false)
    private String phoneNo;

    @Enumerated(EnumType.STRING)
    private WorkersStatus status;

    @ManyToOne
    @JoinColumn(name = "supervisorId")
    private Supervisor supervisor;

    @Column(nullable = false)
    private String photoPath;

    @Column(nullable = false)
    private Date createdAt;

}
