package com.helmet_detection.helmet_detection_backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;

@SpringBootApplication
public class HelmetDetectionBackendApplication {

	public static void main(String[] args) {
		SpringApplication.run(HelmetDetectionBackendApplication.class, args);
		System.out.println("Success");
	}


}
