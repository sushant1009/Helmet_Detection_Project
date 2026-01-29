package com.helmet_detection.helmet_detection_backend.DTO;


import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class DashboardStats {

        private long registeredWorkers;
        private long attendance;
        private long violations;


}
