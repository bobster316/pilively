"""
True 3D Ae Plexus Wallpaper Plugin
Implements proper 3D rendering with perspective and depth of field
"""

import pygame
import numpy as np
import math
import random
from typing import List, Tuple, Optional
from src.core.base_wallpaper import BaseWallpaper

class AePlexus3D(BaseWallpaper):
    """True 3D Ae Plexus implementation with proper depth of field"""
    
    def __init__(self, screen, config, performance_monitor):
        super().__init__(screen, config, performance_monitor)
        
        # Screen properties
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        # 3D Camera properties
        self.camera_distance = 800  # Distance from camera to focus plane
        self.focal_length = 600     # Camera focal length
        self.aperture = 2.8         # Camera aperture (lower = more blur)
        self.focus_distance = 0     # Focus at Z=0 plane
        
        # 3D Space boundaries
        self.space_width = 1200
        self.space_height = 800
        self.space_depth = 1000  # Z from -500 to +500
        
        # Exact color matching from reference
        self.colors = {
            'background': (4, 8, 16),           # Very dark blue-black
            'particle_sharp': (240, 250, 255),  # Bright white-blue (foreground)
            'particle_medium': (180, 220, 245), # Medium blue
            'particle_soft': (120, 160, 200),   # Soft blue (background)
            'connection_bright': (200, 230, 255), # Bright connections
            'connection_medium': (140, 180, 220), # Medium connections
            'connection_soft': (80, 120, 160),    # Soft connections
            'glow_white': (255, 255, 255),       # Pure white glow
            'glow_blue': (150, 200, 255),        # Blue glow
            'atmosphere': (20, 40, 80)           # Atmospheric color
        }
        
        # Particles in 3D space
        self.particles = []
        self.particle_count = 200
        
        # Connection properties
        self.max_connection_distance_3d = 200  # 3D distance
        self.max_connections_per_particle = 8
        
        # Animation
        self.time = 0.0
        self.animation_speed = 0.3  # Slower, smoother movement
        
        # Pre-rendered blur circles for depth of field
        self.blur_circles = {}
        self.create_blur_circles()
        
        # Initialize 3D particles
        self.initialize_3d_particles()
    
    def create_blur_circles(self):
        """Create pre-rendered blur circles for different depths"""
        for blur_radius in range(1, 51, 2):  # 1, 3, 5, ... 49
            circle_surf = pygame.Surface((blur_radius * 4, blur_radius * 4), pygame.SRCALPHA)
            center = (blur_radius * 2, blur_radius * 2)
            
            # Create soft circular gradient
            for r in range(blur_radius, 0, -1):
                alpha = int(120 * (1 - (r / blur_radius)) ** 1.5)
                color = (255, 255, 255, alpha)
                pygame.draw.circle(circle_surf, color, center, r)
            
            self.blur_circles[blur_radius] = circle_surf
    
    def initialize_3d_particles(self):
        """Initialize particles in 3D space"""
        self.particles = []
        
        for _ in range(self.particle_count):
            particle = {
                # 3D position
                'x': random.uniform(-self.space_width/2, self.space_width/2),
                'y': random.uniform(-self.space_height/2, self.space_height/2),
                'z': random.uniform(-self.space_depth/2, self.space_depth/2),
                
                # 3D velocity (very slow for smooth movement)
                'vx': random.uniform(-15, 15),
                'vy': random.uniform(-15, 15),
                'vz': random.uniform(-10, 10),
                
                # Visual properties
                'base_size': random.uniform(2, 6),
                'brightness': random.uniform(0.6, 1.0),
                'pulse_phase': random.uniform(0, 2 * math.pi),
                'pulse_speed': random.uniform(0.5, 1.5),
                
                # Cached 2D projection
                'screen_x': 0,
                'screen_y': 0,
                'screen_size': 0,
                'blur_radius': 0,
                'visible': False,
                'depth_alpha': 1.0
            }
            self.particles.append(particle)
    
    def project_3d_to_2d(self, x, y, z):
        """Project 3D coordinates to 2D screen coordinates"""
        # Perspective projection
        if z >= self.camera_distance - 50:  # Too close to camera
            return None, None, 0
        
        distance_from_camera = self.camera_distance - z
        scale = self.focal_length / distance_from_camera
        
        screen_x = self.center_x + (x * scale)
        screen_y = self.center_y + (y * scale)
        
        return screen_x, screen_y, scale
    
    def calculate_depth_of_field(self, z):
        """Calculate blur radius based on depth of field"""
        # Distance from focus plane
        focus_distance = abs(z - self.focus_distance)
        
        # Circle of confusion calculation
        circle_of_confusion = (focus_distance * self.focal_length) / (self.aperture * (self.camera_distance - focus_distance))
        
        # Convert to pixel blur radius
        blur_radius = min(50, max(0, int(circle_of_confusion * 0.1)))
        
        return blur_radius
    
    def update(self, delta_time: float):
        """Update 3D particle positions and projections"""
        self.time += delta_time * self.animation_speed
        
        for particle in self.particles:
            # Update 3D position with smooth movement
            particle['x'] += particle['vx'] * delta_time
            particle['y'] += particle['vy'] * delta_time
            particle['z'] += particle['vz'] * delta_time
            
            # Wrap around 3D space
            if particle['x'] < -self.space_width/2:
                particle['x'] = self.space_width/2
            elif particle['x'] > self.space_width/2:
                particle['x'] = -self.space_width/2
            
            if particle['y'] < -self.space_height/2:
                particle['y'] = self.space_height/2
            elif particle['y'] > self.space_height/2:
                particle['y'] = -self.space_height/2
            
            if particle['z'] < -self.space_depth/2:
                particle['z'] = self.space_depth/2
            elif particle['z'] > self.space_depth/2:
                particle['z'] = -self.space_depth/2
            
            # Update pulsing
            particle['pulse_phase'] += particle['pulse_speed'] * delta_time
            
            # Project to 2D
            screen_x, screen_y, scale = self.project_3d_to_2d(
                particle['x'], particle['y'], particle['z']
            )
            
            if screen_x is not None:
                particle['screen_x'] = screen_x
                particle['screen_y'] = screen_y
                particle['screen_size'] = particle['base_size'] * scale
                particle['blur_radius'] = self.calculate_depth_of_field(particle['z'])
                particle['visible'] = (0 <= screen_x <= self.width and 
                                     0 <= screen_y <= self.height)
                
                # Depth-based alpha (atmospheric perspective)
                depth_factor = (particle['z'] + self.space_depth/2) / self.space_depth
                particle['depth_alpha'] = 0.3 + 0.7 * (1 - depth_factor)
            else:
                particle['visible'] = False
    
    def get_particle_color_and_alpha(self, particle):
        """Get particle color and alpha based on depth and brightness"""
        base_brightness = particle['brightness']
        pulse_factor = 0.8 + 0.2 * math.sin(particle['pulse_phase'])
        depth_alpha = particle['depth_alpha']
        
        final_brightness = base_brightness * pulse_factor * depth_alpha
        
        # Choose color based on depth and brightness
        if particle['blur_radius'] < 3 and final_brightness > 0.8:
            # Sharp, bright foreground particles
            base_color = self.colors['particle_sharp']
        elif particle['blur_radius'] < 10:
            # Medium depth particles
            base_color = self.colors['particle_medium']
        else:
            # Blurred background particles
            base_color = self.colors['particle_soft']
        
        # Apply brightness
        color = tuple(int(c * final_brightness) for c in base_color)
        alpha = int(255 * final_brightness)
        
        return color, alpha
    
    def draw_particle_3d(self, particle):
        """Draw particle with proper depth of field"""
        if not particle['visible']:
            return
        
        x, y = int(particle['screen_x']), int(particle['screen_y'])
        size = max(1, int(particle['screen_size']))
        blur_radius = particle['blur_radius']
        
        color, alpha = self.get_particle_color_and_alpha(particle)
        
        if blur_radius <= 2:
            # Sharp foreground particle
            # Draw bright glow
            glow_size = size * 3
            for r in range(glow_size, 0, -1):
                glow_alpha = int(alpha * 0.3 * (1 - r/glow_size) ** 2)
                glow_color = (*self.colors['glow_blue'], glow_alpha)
                pygame.draw.circle(self.screen, glow_color, (x, y), r)
            
            # Draw star burst for very bright particles
            if alpha > 200:
                star_length = size * 4
                star_alpha = int(alpha * 0.6)
                star_color = (*self.colors['glow_white'], star_alpha)
                
                # 4-pointed star
                for angle in [0, 45, 90, 135]:
                    rad = math.radians(angle)
                    end_x = x + math.cos(rad) * star_length
                    end_y = y + math.sin(rad) * star_length
                    
                    # Draw star ray with gradient
                    for i in range(star_length):
                        ray_alpha = int(star_alpha * (1 - i/star_length) ** 2)
                        ray_x = x + math.cos(rad) * i
                        ray_y = y + math.sin(rad) * i
                        ray_color = (*self.colors['glow_white'], ray_alpha)
                        pygame.draw.circle(self.screen, ray_color, (int(ray_x), int(ray_y)), max(1, size//2))
            
            # Core particle
            pygame.draw.circle(self.screen, color, (x, y), size)
            
        else:
            # Blurred background particle
            blur_radius = min(49, blur_radius)
            if blur_radius in self.blur_circles:
                blur_surf = self.blur_circles[blur_radius].copy()
                
                # Tint the blur circle
                tint_color = (*color, alpha)
                blur_surf.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
                
                # Position and draw
                blur_rect = blur_surf.get_rect(center=(x, y))
                self.screen.blit(blur_surf, blur_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def calculate_3d_distance(self, p1, p2):
        """Calculate 3D distance between particles"""
        dx = p1['x'] - p2['x']
        dy = p1['y'] - p2['y']
        dz = p1['z'] - p2['z']
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def draw_connection_3d(self, p1, p2, distance_3d):
        """Draw 3D connection with proper depth rendering"""
        if not (p1['visible'] and p2['visible']):
            return
        
        # Calculate connection strength based on 3D distance
        distance_factor = 1.0 - (distance_3d / self.max_connection_distance_3d)
        if distance_factor <= 0:
            return
        
        # Average depth properties
        avg_blur = (p1['blur_radius'] + p2['blur_radius']) / 2
        avg_alpha = (p1['depth_alpha'] + p2['depth_alpha']) / 2
        
        # Connection opacity
        connection_alpha = distance_factor * avg_alpha * 0.8
        
        if connection_alpha < 0.1:
            return
        
        x1, y1 = int(p1['screen_x']), int(p1['screen_y'])
        x2, y2 = int(p2['screen_x']), int(p2['screen_y'])
        
        # Choose connection color based on depth
        if avg_blur < 5:
            base_color = self.colors['connection_bright']
        elif avg_blur < 15:
            base_color = self.colors['connection_medium']
        else:
            base_color = self.colors['connection_soft']
        
        color = tuple(int(c * connection_alpha) for c in base_color)
        line_width = max(1, int(3 * connection_alpha))
        
        # Draw connection with glow
        if avg_blur <= 5:
            # Sharp connection
            # Outer glow
            for width in range(line_width + 4, 0, -1):
                glow_alpha = int(connection_alpha * 255 * 0.2 * (1 - (width - line_width) / 5))
                if glow_alpha > 5:
                    glow_color = (*self.colors['glow_blue'], glow_alpha)
                    pygame.draw.line(self.screen, glow_color, (x1, y1), (x2, y2), width)
            
            # Main line
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), line_width)
            
            # Bright center for strong connections
            if connection_alpha > 0.6:
                center_color = tuple(min(255, int(c * 1.2)) for c in color)
                pygame.draw.line(self.screen, center_color, (x1, y1), (x2, y2), max(1, line_width//2))
        else:
            # Blurred connection
            blur_width = max(1, int(line_width + avg_blur/3))
            alpha = int(connection_alpha * 255 * 0.4)
            blurred_color = (*color, alpha)
            pygame.draw.line(self.screen, blurred_color, (x1, y1), (x2, y2), blur_width)
    
    def render(self):
        """Render the 3D Ae Plexus scene"""
        # Clear with background
        self.screen.fill(self.colors['background'])
        
        # Sort particles by Z-depth (back to front)
        visible_particles = [p for p in self.particles if p['visible']]
        visible_particles.sort(key=lambda p: p['z'])
        
        # Draw connections first (behind particles)
        connection_count = 0
        for i, p1 in enumerate(visible_particles):
            if connection_count > len(visible_particles) * 4:  # Limit connections for performance
                break
                
            connections_for_p1 = 0
            for j, p2 in enumerate(visible_particles[i+1:], i+1):
                if connections_for_p1 >= self.max_connections_per_particle:
                    break
                
                distance_3d = self.calculate_3d_distance(p1, p2)
                if distance_3d < self.max_connection_distance_3d:
                    self.draw_connection_3d(p1, p2, distance_3d)
                    connections_for_p1 += 1
                    connection_count += 1
        
        # Draw particles (back to front for proper alpha blending)
        for particle in visible_particles:
            self.draw_particle_3d(particle)
        
        # Add subtle atmospheric effect
        atmosphere = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        atmosphere.fill((*self.colors['atmosphere'], 15))
        self.screen.blit(atmosphere, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def cleanup(self):
        """Clean up resources"""
        self.blur_circles.clear()
        self.particles.clear()
    
    def get_config_schema(self):
        """Return configuration schema"""
        return {
            "particle_count": {
                "type": "int",
                "default": 200,
                "min": 50,
                "max": 500,
                "description": "Number of 3D particles"
            },
            "animation_speed": {
                "type": "float",
                "default": 0.3,
                "min": 0.1,
                "max": 2.0,
                "description": "Animation speed multiplier"
            },
            "camera_distance": {
                "type": "int",
                "default": 800,
                "min": 400,
                "max": 1200,
                "description": "Camera distance from focus plane"
            },
            "aperture": {
                "type": "float",
                "default": 2.8,
                "min": 1.4,
                "max": 8.0,
                "description": "Camera aperture (lower = more blur)"
            },
            "space_depth": {
                "type": "int",
                "default": 1000,
                "min": 500,
                "max": 2000,
                "description": "3D space depth"
            }
        }

