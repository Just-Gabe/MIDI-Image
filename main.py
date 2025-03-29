from PIL import Image, ImageDraw, ImageFilter, ImageOps
from mido import MidiFile
import numpy as np
import colorsys
import random
from typing import Optional, Dict, Tuple, List
from math import sin, cos, pi

def midi_to_artistic(
    midi_path: str,
    output_path: str,
    img_width: int = 2000,
    img_height: int = 500,
    bg_color: Tuple[int, int, int] = (15, 15, 25),
    style: str = 'classic',  # 'classic', 'watercolor', 'neon', 'particles', 'geometric'
    palette: str = 'hsv',  # 'hsv', 'ocean', 'forest', 'sunset', 'pastel', 'grayscale', 'fire', 'ice'
    enable_vinhetas: bool = True,
    blur_radius: float = 0.5,
    effect_intensity: float = 0.7
) -> Image.Image:
    """Cria representações artísticas de MIDI com estilos visuais distintos."""
    
    # Carregar MIDI
    mid = MidiFile(midi_path)
    
    # Processar mensagens MIDI
    current_time = 0
    active_notes = {}
    events = []
    
    for msg in mid:
        if not msg.is_meta:
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                events.append((current_time, msg.note, msg.velocity, 'start'))
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                events.append((current_time, msg.note, 0, 'end'))
    
    # Calcular durações
    music_notes = []
    for time, note, velocity, typ in events:
        if typ == 'start':
            active_notes[note] = (time, velocity)
        elif typ == 'end' and note in active_notes:
            start_time, vel = active_notes.pop(note)
            duration = time - start_time
            if duration > 0:
                music_notes.append((note, start_time, duration, vel))
    
    if not music_notes:
        return Image.new('RGB', (img_width, img_height), bg_color)
    
    # Normalizar tempo
    total_duration = max(n[1] + n[2] for n in music_notes) or 1
    min_note = min(n[0] for n in music_notes)
    max_note = max(n[0] for n in music_notes)
    note_range = max(max_note - min_note, 1)
    
    # Configurar paleta de cores completa
    def get_color(note, velocity):
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        base_note = note_names[note % 12][0]
        vel_ratio = velocity / 127
        
        if palette == 'hsv':
            hue = (note % 12)/12.0
            saturation = 0.7 + vel_ratio*0.3
            value = 0.6 + vel_ratio*0.4
            return tuple(int(c*255) for c in colorsys.hsv_to_rgb(hue, saturation, value))
        
        elif palette == 'ocean':
            palettes = {
                'C': (20, 60, 130), 'D': (40, 120, 180), 'E': (70, 170, 210),
                'F': (100, 190, 200), 'G': (120, 200, 190), 'A': (150, 210, 170),
                'B': (180, 220, 150)
            }
            base_color = palettes.get(base_note, (200, 200, 200))
            intensity = 0.5 + vel_ratio*0.5
            return tuple(int(c * intensity) for c in base_color)
        
        elif palette == 'forest':
            palettes = {
                'C': (30, 70, 40), 'D': (50, 100, 60), 'E': (80, 130, 80),
                'F': (120, 160, 90), 'G': (160, 190, 100), 'A': (190, 210, 110),
                'B': (210, 220, 120)
            }
            base_color = palettes.get(base_note, (200, 200, 200))
            intensity = 0.6 + vel_ratio*0.4
            return tuple(int(c * intensity) for c in base_color)
        
        elif palette == 'sunset':
            palettes = {
                'C': (180, 50, 70), 'D': (200, 80, 60), 'E': (220, 110, 70),
                'F': (230, 140, 80), 'G': (240, 170, 90), 'A': (250, 200, 120),
                'B': (255, 230, 150)
            }
            base_color = palettes.get(base_note, (255, 255, 200))
            intensity = 0.5 + vel_ratio*0.5
            return tuple(min(255, int(c * intensity)) for c in base_color)
        
        elif palette == 'pastel':
            hue = (note % 12)/12.0
            return tuple(int(c*255) for c in colorsys.hsv_to_rgb(hue, 0.3, 0.9))
        
        elif palette == 'grayscale':
            intensity = 50 + vel_ratio * 205
            return (int(intensity), int(intensity), int(intensity))
        
        elif palette == 'fire':
            heat = vel_ratio * 0.7 + 0.3
            if heat < 0.5:
                return (int(255*heat*2), int(100*heat*2), 0)
            else:
                return (255, int(100 + 155*(heat-0.5)*2), int(100*(heat-0.5)*2))
        
        elif palette == 'ice':
            coldness = vel_ratio * 0.7 + 0.3
            return (int(200*coldness), int(230*coldness), int(255*coldness))
        
        # Default caso a paleta não seja reconhecida
        return (200, 200, 200)
    
    # Estilos visuais
    if style == 'watercolor':
        img = create_watercolor_style(music_notes, img_width, img_height, get_color, total_duration, min_note, note_range)
    elif style == 'neon':
        img = create_neon_style(music_notes, img_width, img_height, get_color, total_duration, min_note, note_range)
    elif style == 'particles':
        img = create_particle_style(music_notes, img_width, img_height, get_color, total_duration, min_note, note_range)
    elif style == 'geometric':
        img = create_geometric_style(music_notes, img_width, img_height, get_color, total_duration, min_note, note_range)
    else:  # classic
        img = create_classic_style(music_notes, img_width, img_height, get_color, total_duration, min_note, note_range)
    
    # Aplicar efeitos pós-processamento
    if blur_radius > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    if enable_vinhetas:
        img = apply_vignette(img, effect_intensity)
    
    img.save(output_path, quality=95)
    return img

# Funções de estilo atualizadas
def create_watercolor_style(notes, width, height, get_color, total_duration, min_note, note_range):
    """Estilo aquarela com bordas difusas"""
    img = Image.new('RGB', (width, height), (240, 240, 235))
    draw = ImageDraw.Draw(img)
    
    for note, start, duration, vel in notes:
        x1 = int((start / total_duration) * width)
        x2 = int(((start + duration) / total_duration) * width)
        y = height - 50 - ((note - min_note) / note_range) * (height - 100)
        
        color = get_color(note, vel)
        for i in range(3):  # Camadas de aquarela
            offset = random.randint(-10, 10)
            radius = random.randint(5, 15)
            draw.ellipse([x1+offset, y-20+offset, x2+offset, y+20+offset], 
                        fill=color, outline=color)
    
    return img.filter(ImageFilter.SMOOTH_MORE)

def create_neon_style(notes, width, height, get_color, total_duration, min_note, note_range):
    """Estilo neon com brilho e glow"""
    img = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    for note, start, duration, vel in notes:
        x1 = int((start / total_duration) * width)
        x2 = int(((start + duration) / total_duration) * width)
        y = height - ((note - min_note) / note_range) * (height - 50)
        
        color = get_color(note, vel)
        # Efeito glow
        for r in range(10, 0, -1):
            alpha = min(255, int(30 * (1 - r/10) * 255))
            glow_color = (*color, alpha) if isinstance(color, tuple) and len(color) == 3 else (255, 255, 255, alpha)
            draw.line([x1, y, x2, y], fill=glow_color, width=r*2)
        # Linha principal neon
        draw.line([x1, y, x2, y], fill=color, width=3)
    
    return img

def create_particle_style(notes, width, height, get_color, total_duration, min_note, note_range):
    """Estilo de partículas com traços"""
    img = Image.new('RGB', (width, height), (10, 10, 20))
    draw = ImageDraw.Draw(img)
    
    for note, start, duration, vel in notes:
        x = int(((start + duration/2) / total_duration) * width)
        y = height - ((note - min_note) / note_range) * (height - 50)
        
        color = get_color(note, vel)
        particle_count = int(vel / 10)
        for _ in range(particle_count):
            px = x + random.randint(-30, 30)
            py = y + random.randint(-30, 30)
            size = random.randint(1, 5)
            draw.ellipse([px-size, py-size, px+size, py+size], fill=color)
    
    return img

def create_geometric_style(notes, width, height, get_color, total_duration, min_note, note_range):
    """Estilo geométrico com formas angulares"""
    img = Image.new('RGB', (width, height), (250, 250, 245))
    draw = ImageDraw.Draw(img)
    
    for note, start, duration, vel in notes:
        x1 = int((start / total_duration) * width)
        x2 = int(((start + duration) / total_duration) * width)
        y = height - ((note - min_note) / note_range) * (height - 50)
        
        color = get_color(note, vel)
        # Formas geométricas alternadas
        if note % 3 == 0:
            draw.rectangle([x1, y-15, x2, y+15], fill=color)
        elif note % 3 == 1:
            draw.polygon([x1, y, x2, y-20, x2, y+20], fill=color)
        else:
            draw.ellipse([x1, y-15, x2, y+15], fill=color)
    
    return img

def create_classic_style(notes, width, height, get_color, total_duration, min_note, note_range):
    """Estilo clássico de piano roll"""
    img = Image.new('RGB', (width, height), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    for note, start, duration, vel in notes:
        x1 = int((start / total_duration) * width)
        x2 = int(((start + duration) / total_duration) * width)
        y1 = height - ((note - min_note) / note_range) * (height - 50)
        y2 = y1 - 20
        
        color = get_color(note, vel)
        draw.rectangle([x1, y1, x2, y2], fill=color)
    
    return img

def apply_vignette(img, intensity):
    """Aplica efeito vinheta"""
    width, height = img.size
    vignette = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    
    max_border = min(width, height) // 3
    for i in range(max_border):
        alpha = int(70 * (1 - i/max_border) * intensity)
        draw.rectangle([i, i, width-i, height-i], outline=(0, 0, 0, alpha))
    
    img = img.convert('RGBA')
    img.alpha_composite(vignette)
    return img.convert('RGB')

# Exemplo de uso
midi_to_artistic(
    'result/result.mid',
    'result/arte_musical.png',
    style='geometric',
    palette='hsv',
    img_width=3000,
    img_height=800,
    effect_intensity=0.9
)