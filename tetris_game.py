#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧱 Тетрис в консоли (Console Tetris)
Классическая игра "Тетрис" для терминала
"""

import random
import time
import os
import keyboard
from threading import Thread
import queue

class TetrisGame:
    def __init__(self):
        self.width = 10
        self.height = 20
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.input_queue = queue.Queue()
        
        # Тетримино (фигуры)
        self.tetrominoes = {
            'I': [['.....',
                   '..#..',
                   '..#..',
                   '..#..',
                   '..#..'],
                  ['.....',
                   '.....',
                   '####.',
                   '.....',
                   '.....']],
            
            'O': [['.....',
                   '.....',
                   '.##..',
                   '.##..',
                   '.....']],
            
            'T': [['.....',
                   '.....',
                   '.#...',
                   '###..',
                   '.....'],
                  ['.....',
                   '.....',
                   '.#...',
                   '.##..',
                   '.#...'],
                  ['.....',
                   '.....',
                   '.....',
                   '###..',
                   '.#...'],
                  ['.....',
                   '.....',
                   '.#...',
                   '##...',
                   '.#...']],
            
            'S': [['.....',
                   '.....',
                   '.##..',
                   '##...',
                   '.....'],
                  ['.....',
                   '.#...',
                   '.##..',
                   '..#..',
                   '.....']],
            
            'Z': [['.....',
                   '.....',
                   '##...',
                   '.##..',
                   '.....'],
                  ['.....',
                   '..#..',
                   '.##..',
                   '.#...',
                   '.....']],
            
            'J': [['.....',
                   '.#...',
                   '.#...',
                   '##...',
                   '.....'],
                  ['.....',
                   '.....',
                   '#....',
                   '###..',
                   '.....'],
                  ['.....',
                   '.##..',
                   '.#...',
                   '.#...',
                   '.....'],
                  ['.....',
                   '.....',
                   '###..',
                   '..#..',
                   '.....']],
            
            'L': [['.....',
                   '..#..',
                   '..#..',
                   '.##..',
                   '.....'],
                  ['.....',
                   '.....',
                   '###..',
                   '#....',
                   '.....'],
                  ['.....',
                   '##...',
                   '.#...',
                   '.#...',
                   '.....'],
                  ['.....',
                   '.....',
                   '..#..',
                   '###..',
                   '.....']]
        }
        
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        
    def get_new_piece(self):
        """Создаёт новую случайную фигуру"""
        shape = random.choice(list(self.tetrominoes.keys()))
        return {
            'shape': shape,
            'rotation': 0,
            'x': self.width // 2 - 2,
            'y': 0
        }
    
    def clear_screen(self):
        """Очищает экран"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_piece_cells(self, piece):
        """Получает координаты клеток фигуры"""
        cells = []
        pattern = self.tetrominoes[piece['shape']][piece['rotation']]
        
        for y, row in enumerate(pattern):
            for x, cell in enumerate(row):
                if cell == '#':
                    cells.append((piece['x'] + x, piece['y'] + y))
        return cells
    
    def is_valid_position(self, piece):
        """Проверяет, можно ли разместить фигуру в данной позиции"""
        cells = self.get_piece_cells(piece)
        
        for x, y in cells:
            if x < 0 or x >= self.width or y >= self.height:
                return False
            if y >= 0 and self.board[y][x] != 0:
                return False
        return True
    
    def place_piece(self, piece):
        """Размещает фигуру на доске"""
        cells = self.get_piece_cells(piece)
        
        for x, y in cells:
            if y >= 0:
                self.board[y][x] = 1
    
    def clear_lines(self):
        """Очищает заполненные линии"""
        lines_to_clear = []
        
        for y in range(self.height):
            if all(self.board[y]):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [0 for _ in range(self.width)])
        
        lines_count = len(lines_to_clear)
        if lines_count > 0:
            self.lines_cleared += lines_count
            # Очки за линии (больше линий одновременно = больше очков)
            points = [0, 100, 300, 500, 800][lines_count] * self.level
            self.score += points
            self.level = self.lines_cleared // 10 + 1
    
    def draw_board(self):
        """Рисует игровое поле"""
        self.clear_screen()
        
        # Создаём копию доски для отображения
        display_board = [row[:] for row in self.board]
        
        # Добавляем текущую фигуру на доску
        if not self.game_over:
            cells = self.get_piece_cells(self.current_piece)
            for x, y in cells:
                if 0 <= y < self.height and 0 <= x < self.width:
                    display_board[y][x] = 2
        
        print('🧱 ТЕТРИС')
        print('┌' + '──' * self.width + '┐')
        
        for row in display_board:
            line = '│'
            for cell in row:
                if cell == 0:
                    line += '  '  # Пустая клетка
                elif cell == 1:
                    line += '██'  # Размещённый блок
                else:  # cell == 2
                    line += '▓▓'  # Падающий блок
            line += '│'
            print(line)
        
        print('└' + '──' * self.width + '┘')
        print(f'Счёт: {self.score}')
        print(f'Линий: {self.lines_cleared}')
        print(f'Уровень: {self.level}')
        print('A/D - влево/вправо | S - ускорить падение')
        print('W - поворот | ESC - выход')
    
    def handle_input(self):
        """Обработка ввода в отдельном потоке"""
        while not self.game_over:
            try:
                if keyboard.is_pressed('a') or keyboard.is_pressed('left'):
                    self.input_queue.put('left')
                elif keyboard.is_pressed('d') or keyboard.is_pressed('right'):
                    self.input_queue.put('right')
                elif keyboard.is_pressed('s') or keyboard.is_pressed('down'):
                    self.input_queue.put('down')
                elif keyboard.is_pressed('w') or keyboard.is_pressed('up'):
                    self.input_queue.put('rotate')
                elif keyboard.is_pressed('esc'):
                    self.game_over = True
                time.sleep(0.1)
            except:
                pass
    
    def process_input(self):
        """Обрабатывает накопленный ввод"""
        processed = set()  # Избегаем повторной обработки одинаковых команд
        
        while not self.input_queue.empty():
            try:
                command = self.input_queue.get_nowait()
                if command in processed:
                    continue
                processed.add(command)
                
                new_piece = self.current_piece.copy()
                
                if command == 'left':
                    new_piece['x'] -= 1
                elif command == 'right':
                    new_piece['x'] += 1
                elif command == 'down':
                    new_piece['y'] += 1
                elif command == 'rotate':
                    new_piece['rotation'] = (new_piece['rotation'] + 1) % len(self.tetrominoes[new_piece['shape']])
                
                if self.is_valid_position(new_piece):
                    self.current_piece = new_piece
                    
            except queue.Empty:
                break
    
    def update_game(self):
        """Обновляет состояние игры"""
        # Пытаемся опустить фигуру на одну позицию
        new_piece = self.current_piece.copy()
        new_piece['y'] += 1
        
        if self.is_valid_position(new_piece):
            self.current_piece = new_piece
        else:
            # Фигура не может опуститься - размещаем её
            self.place_piece(self.current_piece)
            self.clear_lines()
            
            # Создаём новую фигуру
            self.current_piece = self.next_piece
            self.next_piece = self.get_new_piece()
            
            # Проверяем, можно ли разместить новую фигуру
            if not self.is_valid_position(self.current_piece):
                self.game_over = True
    
    def get_fall_speed(self):
        """Возвращает скорость падения в зависимости от уровня"""
        return max(0.1, 0.8 - (self.level - 1) * 0.1)
    
    def run(self):
        """Основной игровой цикл"""
        print("🧱 Добро пожаловать в Тетрис!")
        print("Нажмите любую клавишу для начала...")
        input()
        
        # Запускаем поток для обработки ввода
        input_thread = Thread(target=self.handle_input, daemon=True)
        input_thread.start()
        
        last_fall = time.time()
        
        while not self.game_over:
            self.draw_board()
            self.process_input()
            
            # Автоматическое падение фигур
            current_time = time.time()
            if current_time - last_fall > self.get_fall_speed():
                self.update_game()
                last_fall = current_time
            
            time.sleep(0.05)  # Небольшая пауза для снижения нагрузки на CPU
        
        self.clear_screen()
        print("🎮 ИГРА ОКОНЧЕНА!")
        print(f"💯 Финальный счёт: {self.score}")
        print(f"📏 Линий очищено: {self.lines_cleared}")
        print(f"🎯 Достигнутый уровень: {self.level}")
        print("Нажмите Enter для выхода...")
        input()

def main():
    """Главная функция"""
    try:
        game = TetrisGame()
        game.run()
    except KeyboardInterrupt:
        print("\n\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("Убедитесь, что установлен модуль keyboard: pip install keyboard")

if __name__ == "__main__":
    main()