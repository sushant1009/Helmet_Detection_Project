package com.helmet_detection.helmet_detection_backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class HelmetDetectionBackendApplication{

	public static void main(String[] args) {
		SpringApplication.run(HelmetDetectionBackendApplication.class, args);
		System.out.println("Success");
	}
}