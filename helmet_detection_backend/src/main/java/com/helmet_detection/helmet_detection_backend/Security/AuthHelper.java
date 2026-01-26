package com.helmet_detection.helmet_detection_backend.Security;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ResponseStatusException;

import java.util.Arrays;
import java.util.Map;
import java.util.Optional;

@Component
public class AuthHelper {


    private final Map<String, String> tokenStore;

    public AuthHelper(Map<String, String> tokenStore) {
        this.tokenStore = tokenStore;
    }

    public String getUsernameFromRequest(HttpServletRequest request) {
        String token = Arrays.stream(Optional.ofNullable(request.getCookies())
                        .orElse(new Cookie[0]))
                .filter(c -> "auth_token".equals(c.getName()))
                .map(Cookie::getValue)
                .findFirst()
                .orElse(null);

        if (token == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Not logged in");
        }

        String email = tokenStore.get(token);
        if (email == null) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid token");
        }

        return email;
    }
}
