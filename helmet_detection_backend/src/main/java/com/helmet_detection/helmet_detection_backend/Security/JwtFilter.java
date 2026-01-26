package com.helmet_detection.helmet_detection_backend.Security;

import com.helmet_detection.helmet_detection_backend.Service.CustomUserDetailsService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class JwtFilter extends OncePerRequestFilter {

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private CustomUserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain)
            throws ServletException, IOException, java.io.IOException {

        String header = request.getHeader("Authorization");

        if (header != null && header.startsWith("Bearer ")) {

            String token = header.substring(7);

            if (jwtUtil.isTokenValid(token)) {

                String username = jwtUtil.extractUsername(token);
                UserDetails userDetails =
                        userDetailsService.loadUserByUsername(username);

                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                userDetails,
                                null,
                                userDetails.getAuthorities());

                SecurityContextHolder.getContext()
                        .setAuthentication(authentication);
            }
        }
        filterChain.doFilter(request, response);
    }
}
//@Component
//@RequiredArgsConstructor
//public class JwtFilter extends OncePerRequestFilter {
//
//    private final JwtUtil jwtUtil;
//    private final CustomUserDetailsService userDetailsService;
//
//    @Override
//    protected void doFilterInternal(
//            HttpServletRequest request,
//            HttpServletResponse response,
//            FilterChain filterChain)
//            throws ServletException, IOException {
//
//        String header = request.getHeader("Authorization");
//
//        if (header != null && header.startsWith("Bearer ")) {
//            String token = header.substring(7);
//            String username = jwtUtil.extractUsername(token);
//
//            if (username != null &&
//                    SecurityContextHolder.getContext().getAuthentication() == null) {
//
//                UserDetails userDetails =
//                        userDetailsService.loadUserByUsername(username);
//
//                if (jwtUtil.isTokenValid(token)) {
//                    UsernamePasswordAuthenticationToken authToken =
//                            new UsernamePasswordAuthenticationToken(
//                                    userDetails,
//                                    null,
//                                    userDetails.getAuthorities());
//
//                    SecurityContextHolder.getContext()
//                            .setAuthentication(authToken);
//                }
//            }
//        }
//
//        filterChain.doFilter(request, response);
//    }
//}
