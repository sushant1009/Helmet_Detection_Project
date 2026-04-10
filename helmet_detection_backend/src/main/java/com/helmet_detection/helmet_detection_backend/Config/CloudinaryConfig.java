package com.helmet_detection.helmet_detection_backend.Config;


import com.cloudinary.Cloudinary;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.HashMap;
import java.util.Map;

@Configuration
public class CloudinaryConfig {

        private static Cloudinary cloudinary;


        @Value("${cloudinary.cloud.name}")
        private  String CLOUD_NAME ;
        @Value("${cloudinary.api.key}")
        private   String API_KEY ;
        @Value("${cloudinary.api.secret}")
        private  String API_SECRET;

        /**
         * Returns a single shared Cloudinary instance (Singleton pattern).
         */
        @Bean
        public Cloudinary getInstance() {
            if (cloudinary == null) {
                Map<String, String> config = new HashMap<>();
                config.put("cloud_name", CLOUD_NAME);
                config.put("api_key",    API_KEY);
                config.put("api_secret", API_SECRET);
                config.put("secure",     "true");
                cloudinary = new Cloudinary(config);
            }
            return cloudinary;
        }
}

