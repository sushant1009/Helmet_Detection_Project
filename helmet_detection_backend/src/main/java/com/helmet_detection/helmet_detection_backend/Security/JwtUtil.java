package com.helmet_detection.helmet_detection_backend.Security;


import com.helmet_detection.helmet_detection_backend.Entity.Supervisor;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.security.Key;
import java.util.Date;

@Component
public class JwtUtil {

    private static final String SECRET_KEY =
            "mySecretKey123456789012345678901234"; // 32+ chars

    private final Key key =
            Keys.hmacShaKeyFor(SECRET_KEY.getBytes());

    public String generateToken(Supervisor supervisor) {
        System.out.println(supervisor.getEmail()+" token");
        return Jwts.builder()
                .subject(String.valueOf(supervisor.getEmail()))
                .claim("role", supervisor.getRole())
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + (3*3600000)))
                .signWith(key)
                .compact();
    }

    public String extractUsername(String token) {
        return extractClaims(token).getSubject();
    }

    public String extractRole(String token) {
        return extractClaims(token).get("role", String.class);
    }

    private Claims extractClaims(String token) {
        return Jwts.parser()
                .verifyWith((SecretKey) key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public boolean isTokenValid(String token) {
        try {
            extractClaims(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

}
//@Component
//public class JwtUtil {
//
//    private static final String SECRET_KEY =
//            "mySecretKey123456789012345678901234";
//
//    private final Key key =
//            Keys.hmacShaKeyFor(SECRET_KEY.getBytes());
//
//    public String generateToken(Supervisor supervisor) {
//        return Jwts.builder()
//                .subject(supervisor.getEmail())
//                .claim("role", supervisor.getRole())
//                .issuedAt(new Date())
//                .expiration(new Date(System.currentTimeMillis() + 3 * 60 * 60 * 1000))
//                .signWith(key)
//                .compact();
//    }
//
//    public String extractUsername(String token) {
//        return extractClaims(token).getSubject();
//    }
//
//    public boolean isTokenValid(String token, UserDetails userDetails) {
//        final String username = extractUsername(token);
//        return username.equals(userDetails.getUsername())
//                && !isTokenExpired(token);
//    }
//
//    private boolean isTokenExpired(String token) {
//        return extractClaims(token).getExpiration().before(new Date());
//    }
//
//    private Claims extractClaims(String token) {
//        return Jwts.parser()
//                .verifyWith((SecretKey) key)
//                .build()
//                .parseSignedClaims(token)
//                .getPayload();
//    }
//}
//
