# -*- coding: utf-8 -*-
"""
Ming Dynasty RPG - Enemy Renderer
Handles drawing and rendering of all enemies and bosses on the screen.
"""

import pygame

def draw_enemies(surface: pygame.Surface, enemies: list, camera_x: int, camera_y: int, 
                 start_col: int, end_col: int, start_row: int, end_row: int, 
                 enemy_sprites: dict, font_small: pygame.font.Font, TILE_SIZE: int, 
                 COLOR_GOLD: tuple, COLOR_RED: tuple) -> None:
    """
    Draws all enemies within the camera view and displays their name tags if they are bosses.
    """
    for enemy in enemies:
        if start_col <= enemy.grid_x < end_col and start_row <= enemy.grid_y < end_row:
            enemy.draw(surface, camera_x, camera_y, enemy_sprites)
            
            # Draw Boss or Ultimate Boss tag/indicator above their heads
            if enemy.is_boss:
                enemy_screen_x = enemy.pixel_x - camera_x
                enemy_screen_y = enemy.pixel_y - camera_y
                
                tag_color = COLOR_GOLD if enemy.is_ultimate_boss else COLOR_RED
                tag_text = f"👑 {enemy.name}" if enemy.is_ultimate_boss else f"👹 {enemy.name}"
                tag_surf = font_small.render(tag_text, True, tag_color)
                
                # Background for readability
                bg_rect = pygame.Rect(
                    enemy_screen_x + TILE_SIZE // 2 - tag_surf.get_width() // 2 - 4,
                    enemy_screen_y - 20,
                    tag_surf.get_width() + 8,
                    tag_surf.get_height() + 2
                )
                pygame.draw.rect(surface, (16, 16, 24, 200), bg_rect)
                pygame.draw.rect(surface, tag_color, bg_rect, 1)
                
                surface.blit(tag_surf, (enemy_screen_x + TILE_SIZE // 2 - tag_surf.get_width() // 2, enemy_screen_y - 20))
