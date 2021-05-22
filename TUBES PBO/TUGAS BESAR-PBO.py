import pygame
import sys
import random
from pygame.math import *
from pygame.sprite import Sprite

percepatan_biasa = 200
Ular_Ukuran = 20
Ular_Pinggiran = 2
Ukuran_Persegi = Ular_Ukuran + Ular_Pinggiran
X_Persegi = 42
Y_Persegi = 24
GAME_Pinggiran = 50
Papan_Ketebalan = 2
Papan_Lapisan = 5

class Makanan():
    def __init__(self):
        self.Koordinasi = (0,0)

    def perbarui(self, Ular_Persegi, game_Persegi):
        Tersedia_Persegi = list(game_Persegi.difference(Ular_Persegi))
        self.Koordinasi = random.choice(Tersedia_Persegi)

    def get_koordinasi(self):
        return self.Koordinasi

    def draw(self, surface):
        pygame.draw.circle(surface, pygame.Color("red"), self.Koordinasi, 5)

class PapanGame():
    def __init__(self, first_tile_center):
        x = first_tile_center[0] - ((Ular_Ukuran / 2) + Papan_Ketebalan + Papan_Lapisan)
        y = first_tile_center[1] - ((Ular_Ukuran / 2) + Papan_Ketebalan + Papan_Lapisan)
        Lebar = (X_Persegi * Ukuran_Persegi) + (2 * Papan_Lapisan) + Papan_Ketebalan
        Tinggi = (Y_Persegi * Ukuran_Persegi) + (2 * Papan_Lapisan) + Papan_Ketebalan
        self.area = (x, y, Lebar, Tinggi)

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color("green"), self.area, Papan_Ketebalan)


class Segment(Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface([Ular_Ukuran, Ular_Ukuran])
        self.image.fill(pygame.Color('white'))
        self.rect = self.image.get_rect(center=center)

class Ular():
    def __init__(self, Panjang, mulai_center):
        self.segments = []
        self.sprites = pygame.sprite.Group()
        self.percepatan = Vector2(Ukuran_Persegi, 0)
        self.Pakai_Key = {
            pygame.K_UP: Vector2(0, -22),
            pygame.K_DOWN: Vector2(0, 22),
            pygame.K_LEFT: Vector2(-22, 0),
            pygame.K_RIGHT: Vector2(22, 0)
        }
        self.processing_event = False
        for i in range(Panjang):
            x = mulai_center[0] - (Ukuran_Persegi * i)
            y = mulai_center[1]
            segment = Segment((x, y))
            self.sprites.add(segment)
            self.segments.append(segment)

    def Kepala_Baru(self):
        center = self.segments[0].rect.center
        x = center[0] + self.percepatan[0]
        y = center[1] + self.percepatan[1]
        return Segment((x, y))

    def handle_input(self, key):
        if not self.processing_event:
            self.processing_event = True
            if key in self.Pakai_Key and not self.Pakai_Key[key] == -self.percepatan:
                self.percepatan = self.Pakai_Key[key]

    def bertabrakan(self, game_Persegi):
        occupying = self.get_semua_koordinasi()
        if len(self.sprites.sprites()) > len(occupying):
            return True
        remainder = occupying.difference(game_Persegi)
        if len(remainder) > 0:
            return True
        
        return False

    def get_semua_koordinasi(self):
        result = set()
        for segment in self.segments:
            result.add(segment.rect.center)
        return result

    def Tumbuh(self):
        Ekor = self.segments[-1]
        new_segment = Segment(Ekor.rect.center)
        self.segments.append(new_segment)
        self.sprites.add(new_segment)
    
    def get_kepala_center(self):
        return self.segments[0].rect.center

    def perbarui(self):
        Ekor = self.segments.pop()
        self.sprites.remove(Ekor)

        Kepala_Baru = self.Kepala_Baru()
        self.segments.insert(0, Kepala_Baru)
        self.sprites.add(Kepala_Baru)
        self.processing_event = False

    def draw(self, surface):
        self.sprites.draw(surface)

class  StatusDasar(object):
    def __init__(self):
        self.done = False
        self.quit = False
        self.status_Selanjutnya = None
        self.screen_rect = pygame.display.get_surface().get_rect()
        self.persist = {}
        self.font = pygame.font.Font(None, 36)

    def memulai(self, persistent):
        self.persist = persistent

    def get_event(self, event):
        pass

    def perbarui(self, dt):
        pass

    def draw(self, surface):
        pass

class GameBerakhir(StatusDasar):
    def __init__(self):
        super(GameBerakhir, self).__init__()
        self.title = self.font.render("Permainan Berakhir", True, pygame.Color("white"))
        self.title_rect = self.title.get_rect(center=self.screen_rect.center)
        self.instructions = self.font.render("Pencet spasi untuk ke memulai kembali, atau enter untuk ke main menu", True, pygame.Color("white"))
        instructions_center = (self.screen_rect.center[0], self.screen_rect.center[1] +  150)
        self.instructions_rect = self.instructions.get_rect(center=instructions_center)

    def memulai(self, persistent):
        Skor = persistent['Skor']
        self.final_Skor = self.font.render(f"Skor akhirmu adalah {Skor}", True, pygame.Color("Red"))
        final_Skor_center = (self.screen_rect.center[0], self.screen_rect.center[1] +  50)
        self.final_Skor_rect = self.final_Skor.get_rect(center=final_Skor_center)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                self.status_Selanjutnya = "MENU"
                self.done = True
            elif event.key == pygame.K_SPACE:
                self.status_Selanjutnya = "GAMEPLAY"
                self.done = True
            elif event.key == pygame.K_ESCAPE:
                self.quit = True

    def draw(self, surface):
        surface.fill(pygame.Color("black"))
        surface.blit(self.title, self.title_rect)
        surface.blit(self.final_Skor, self.final_Skor_rect)
        surface.blit(self.instructions, self.instructions_rect)

class Gameplay(StatusDasar):
    def __init__(self):
        super(Gameplay, self).__init__()
        self.status_Selanjutnya = "GAME_OVER"
        self.title_font = pygame.font.Font(None, 56)
        self.game_title_text = self.title_font.render("Cacing besar Alaska", True, pygame.Color("blue"))
        game_title_center = (self.screen_rect.center[0], 80)
        self.game_title_rect = self.game_title_text.get_rect(center=game_title_center)
        game_width, game_Tinggi = pygame.display.get_surface().get_size()
        self.x_Awal = int(GAME_Pinggiran + (Ular_Ukuran / 2))
        self.y_Awal = int((game_Tinggi - ((Y_Persegi * Ukuran_Persegi) + GAME_Pinggiran)) + (Ular_Ukuran / 2))
        self.Papan = PapanGame ((self.x_Awal, self.y_Awal))
        x_Akhir = int(game_width - GAME_Pinggiran)
        y_Akhir = int(game_Tinggi - GAME_Pinggiran)
        self.Persegi = set()
        for x in range(self.x_Awal, x_Akhir, Ukuran_Persegi):
            for y in range(self.y_Awal, y_Akhir, Ukuran_Persegi):
                self.Persegi.add((x, y))

    def memulai(self, persistent):
        self.persist["Skor"] = 0
        self.perbarui_kecepatan = percepatan_biasa
        self.Skor = 0
        self.difficulty_level = 1
        Ular_x = self.x_Awal + (4 * Ukuran_Persegi)
        Ular_y = self.y_Awal + (3 * Ukuran_Persegi)
        self.Ular = Ular(2, (Ular_x, Ular_y))
        self.Makanan = Makanan()
        self.Makanan.perbarui(self.Ular.get_semua_koordinasi(), self.Persegi)

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.done = True
            else:
                self.Ular.handle_input(event.key)

    def check_Makanan(self):
        kepala_center = self.Ular.get_kepala_center()
        Makanan_Koordinasi = self.Makanan.get_koordinasi()
        if kepala_center == Makanan_Koordinasi:
            self.Ular.Tumbuh()
            self.Makanan.perbarui(self.Ular.get_semua_koordinasi(), self.Persegi)
            self.Skor += 1
            self.persist["Skor"] = self.Skor
            if self.Skor % 10 == 0 and not self.Skor == 0:
                self.difficulty_level += 1

    def perbarui(self, dt):
        self.perbarui_kecepatan -= dt
        if self.perbarui_kecepatan <= 0:
            self.Ular.perbarui()
            if self.Ular.bertabrakan(self.Persegi):
                self.done = True
            self.check_Makanan()
            self.perbarui_kecepatan = (percepatan_biasa / self.difficulty_level)

    def draw(self, surface):
        surface.fill(pygame.Color("black"))
        surface.blit(self.game_title_text, self.game_title_rect)
        Skor_text = self.font.render(f"Skor : {self.Skor}", True, pygame.Color("red"))
        surface.blit(Skor_text, (50, 90))
        self.Papan.draw(surface)
        self.Ular.draw(surface)
        self.Makanan.draw(surface)

class Menu(StatusDasar):
    def __init__(self):
        super(Menu, self).__init__()
        self.active_index = 0
        self.options = ["MULAI", "KELUAR"]
        self.status_Selanjutnya = "GAMEPLAY"

    def render_text(self, index):
        color = pygame.Color("red") if index == self.active_index else pygame.Color("white")
        return self.font.render(self.options[index], True, color)

    def get_text_posisi(self, text, index):
        center = (self.screen_rect.center[0], self.screen_rect.center[1] + (index * 50))
        return text.get_rect(center=center)

    def handle_action(self):
        if self.active_index == 0:
            self.done = True
        elif self.active_index == 1:
            self.quit = True

    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.active_index = 1 if self.active_index <= 0 else 0
            elif event.key == pygame.K_DOWN:
                self.active_index = 0 if self.active_index >= 1 else 1
            elif event.key == pygame.K_RETURN:
                self.handle_action()

    def draw(self, surface):
        surface.fill(pygame.Color("black"))
        for index, option in enumerate(self.options):
            text_render = self.render_text(index)
            surface.blit(text_render, self.get_text_posisi(text_render, index))

class Splash(StatusDasar):
    def __init__(self):
        super(Splash, self).__init__()
        self.title_font = pygame.font.Font(None, 120)
        self.title = self.title_font.render("Cacing Besar Alaska", True, pygame.Color("blue"))
        self.title_rect = self.title.get_rect(center=self.screen_rect.center)
        self.status_Selanjutnya = "MENU"
        self.time_active = 0

    def perbarui(self, dt):
        self.time_active += dt
        if self.time_active >= 3000:
            self.done = True

    def draw(self, surface):
        surface.fill(pygame.Color("black"))
        surface.blit(self.title, self.title_rect)

class Game(object):
    def __init__(self, screen, list_status, start_status):
        self.done = False
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.list_status = list_status
        self.status_name = start_status
        self.status = self.list_status[self.status_name]

    def event_loop(self):
        for event in pygame.event.get():
            self.status.get_event(event)

    def flip_status(self):
        status_sekarang = self.status_name
        status_Selanjutnya = self.status.status_Selanjutnya
        self.status.done = False
        self.status_name = status_Selanjutnya
        persistent = self.status.persist
        self.status = self.list_status[self.status_name]
        self.status.memulai(persistent)

    def perbarui(self, dt):
        if self.status.quit:
            self.done = True
        elif self.status.done:
            self.flip_status()
        self.status.perbarui(dt)

    def draw(self):
        self.status.draw(self.screen)

    def run(self):
        while not self.done:
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.perbarui(dt)
            self.draw()
            pygame.display.update()

pygame.init()
screen = pygame.display.set_mode((1024, 768))
list_status = {
    "MENU": Menu(),
    "SPLASH": Splash(),
    "GAMEPLAY": Gameplay(),
    "GAME_OVER": GameBerakhir(),
}

game = Game(screen, list_status, "SPLASH")
game.run()

pygame.quit()
sys.exit()