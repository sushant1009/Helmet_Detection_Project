package com.helmet_detection.helmet_detection_backend.DTO;

import com.helmet_detection.helmet_detection_backend.Entity.WorkersStatus;
import lombok.AllArgsConstructor;
import lombok.Data;
import java.util.Date;

@Data
@AllArgsConstructor
public class WorkersDTO {

    private Long workerId;

    private String fullName;

    private String aadharNo;

    private String email;

    private Date dob;

    private String phoneNo;

    private WorkersStatus status;

    private Long supervisor;

    private String photoPath;

}
