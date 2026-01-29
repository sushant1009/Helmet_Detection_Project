package com.helmet_detection.helmet_detection_backend.Entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.RequiredArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Date;

@Data
@Entity
@RequiredArgsConstructor
public class Violations {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long voilationId;

    @Column(nullable = false)
    private LocalDate date;

    @Column(nullable = false)
    private LocalDateTime time;

    @Column(nullable = false)
    private Float Score;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "worker_id", referencedColumnName = "workerId")
    private Workers worker;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "supervisor_id", referencedColumnName = "supervisorId")
    private Supervisor supervisor;

}
