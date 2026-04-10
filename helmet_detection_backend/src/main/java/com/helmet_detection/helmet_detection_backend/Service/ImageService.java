package com.helmet_detection.helmet_detection_backend.Service;

import org.springframework.stereotype.Service;


import com.cloudinary.Cloudinary;
import com.cloudinary.utils.ObjectUtils;

import java.io.File;
import java.time.LocalDate;
import java.util.Map;


@Service
public class ImageService {

    private final Cloudinary cloudinary ;

    public ImageService(Cloudinary cloudinary) {
        this.cloudinary = cloudinary;
    }

    public String uploadWorkerImage(byte[] imageBytes, String workerId) {
        try {
            Map result = cloudinary.uploader().upload(
                    imageBytes,
                    ObjectUtils.asMap(
                            "folder",    "workers",
                            "public_id", workerId,
                            "overwrite", true
                    )
            );

            String url = result.get("secure_url").toString();
            return url;

        } catch (Exception e) {
            System.err.println("Failed to upload worker image: " + e.getMessage());
            return null;
        }
    }

    public String uploadViolationImage(byte[] imageBytes, String violationId, LocalDate date) {
        try {
            Map result = cloudinary.uploader().upload(
                    imageBytes,
                    ObjectUtils.asMap(
                            "folder",    "violations/" + date,
                            "public_id", violationId,
                            "overwrite", true
                    )
            );

            String url = result.get("secure_url").toString();
            System.out.println(" Violation image uploaded: " + url);
            return url;

        } catch (Exception e) {
            System.err.println(" Failed to upload violation image: " + e.getMessage());
            return null;
        }
    }

    public boolean deleteWorkerImage(String workerId) {
        try {
            String publicId = "workers/" + workerId;

            Map result = cloudinary.uploader().destroy(publicId, ObjectUtils.emptyMap());

            String status = result.get("result").toString();
            if (status.equals("ok")) {
                System.out.println("Worker image deleted: " + publicId);
                return true;
            } else {
                System.out.println("Image not found or already deleted: " + publicId);
                return false;
            }

        } catch (Exception e) {
            System.err.println(" Failed to delete worker image: " + e.getMessage());
            return false;
        }
    }


    public boolean deleteViolationImage(String violationId, String date) {
        try {
            // public_id = "violations/2025-02/violation_001"
            String publicId = "violations/" + date + "/" + violationId;

            Map result = cloudinary.uploader().destroy(publicId, ObjectUtils.emptyMap());

            String status = result.get("result").toString();
            if (status.equals("ok")) {
                System.out.println("Violation image deleted: " + publicId);
                return true;
            } else {
                System.out.println("Image not found or already deleted: " + publicId);
                return false;
            }

        } catch (Exception e) {
            System.err.println("Failed to delete violation image: " + e.getMessage());
            return false;
        }
    }
}