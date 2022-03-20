from copy import deepcopy
from miscellaneous import *
from os import getcwd, path
from pathlib import Path
import pygame
import random
import sys
from typing import List, Tuple

# TODO: docstrings, testing

class WordleUI:
    """CLI optional kwargs
    - mode = single player or multiplayer
    - letters = 4 to 7
    - language = english or français
    - text_directory_path = folder path
    - allowed_guesses_file_name = file name
    - possible_solutions_file_name = file name"""
    FPS: int = 30
    TEXT_TIMER: int = 2
    BASE_N_LETTERS: int = 5
    BASE_N_ROWS: int = 6
    # colors
    SOLID_BLACK: Tuple[int] = (0, 0, 0)
    BLACK: Tuple[int] = (33, 33, 33)
    WHITE: Tuple[int] = (255, 255, 255)
    LIGHT_GREY: Tuple[int] = (216, 216, 216)
    GREY: Tuple[int] = (134, 136, 138)
    DARK_GREY: Tuple[int] = (147, 149, 152)
    RED: Tuple[int] = (255, 0, 0)
    GREEN: Tuple[int] = (106, 170, 100)
    YELLOW: Tuple[int] = (201, 180, 88)
    # text
    INVALID_WORD_STR: dict = {"english":"Not in word list",
                              "français":"Pas dans la liste de mots"}
    INVALID_LEN_STR: dict =  {"english":"Not enough letters",
                              "français":"Pas assez de lettres"}
    GAME_WON_STR: dict = {"english":"You won! Press enter to play again or escape to exit", 
                          "français":"Tu as gagné! Appuyez sur Entrée pour rejouer ou Echap pour quitter"}
    GAME_LOSS_STR: dict = {1:{"english":"The answer was",
                              "français":"La solution était"},
                           2:{"english":"press enter to play again or escape to exit",
                              "français":"appuyez sur Entrée pour rejouer ou Echap pour quitter"}}
    TITLE_STR: dict = {"english":"Variable Length Multilingual Multiplayer Wordle", 
                       "français":"Wordle multijoueur multilingue de longueur variable"}
    AVAILABLE_LANGUAGES: List[str] = ["english", "français"]
    AVAILABLE_MODES: List[str] = ["single player", "two player"]
    PLAYER_VALID_KWARGS_KEYS: List[str] = ["mode", "letters", 
                                            "rows", "language", 
                                            "text_directory", "text_files"]
    
    # max/min game settings
    MAX_N_ROWS: int = 8
    MIN_N_ROWS: int = 1
    MAX_N_LETTERS: int = 7
    MIN_N_LETTERS: int = 4

    # singleton logic 
    def __new__(cls, **kwargs):
        it: object = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.__init__(**kwargs)
        return it

    def __init__(self, **kwargs):
        self._validate_kwargs(**kwargs)
        pygame.init()
        pygame.display.set_caption("Wordle Clone Variant")
        self._define_new_game_attributes()
        self._setup_display_attributes()
        self._setup_language()
        self._play_mode()

    def _setup_language(self):
        self.title: str = self.TITLE_STR[self.LANGUAGE]
        self.invalid_len_str: str = self.INVALID_LEN_STR[self.LANGUAGE]
        self.invalid_word_str: str = self.INVALID_WORD_STR[self.LANGUAGE]
        self.game_won_str: str = self.GAME_WON_STR[self.LANGUAGE]
        self.game_loss_str1: str = self.GAME_LOSS_STR[1][self.LANGUAGE]
        self.game_loss_str2: str = self.GAME_LOSS_STR[2][self.LANGUAGE]

    def _play_mode(self):
        if self.MODE == "single player":
            self._solo_game()
        elif self.MODE == "two player":
            self._two_player_game()
            pass
        else:
            # possible future modes
            pass

    def _two_player_game(self):
        game_is_running: bool = True
        self._create_two_player_wordle_grids()
        while game_is_running:
            # background
            self._screen.fill(self.WHITE)
            self._draw_grid(self._player1_grid)
            self._draw_grid(self._player2_grid)
            self._draw_underlined_var_length_title()
            self._switch_grid_check()
            self._capture_player_events()
            self._update_game_text()
            self._render_current_guess_letters(self._current_grid)
            self._render_past_attempts(self._player1_grid)
            self._render_past_attempts(self._player2_grid)
            self._render_blocked_boxes()
            self._check_game_state()
            pygame.display.update()
            self._clock.tick(self.FPS)

    def _render_blocked_boxes(self):
        for row_n in range(0, self.N_ROWS):
            p1_x = self._player1_grid[row_n][self._blocked_box_i]["x"]
            p1_y = self._player1_grid[row_n][self._blocked_box_i]["y"]
            p2_x = self._player2_grid[row_n][self._blocked_box_i]["x"]
            p2_y = self._player2_grid[row_n][self._blocked_box_i]["y"]
            if self._get_grid_row_word(self._player1_grid[row_n]) != self._answer:
                p1_black_box_rect = pygame.Rect((p1_x, p1_y), (self.BOX_WIDTH, self.BOX_HEIGHT))
                pygame.draw.rect(self._screen, self.SOLID_BLACK, p1_black_box_rect)
            if self._get_grid_row_word(self._player2_grid[row_n]) != self._answer:
                p2_black_box_rect = pygame.Rect((p2_x, p2_y), (self.BOX_WIDTH, self.BOX_HEIGHT))
                pygame.draw.rect(self._screen, self.SOLID_BLACK, p2_black_box_rect)

    def _switch_grid_check(self):
        # check to see which grid should be in play, switch if necessary
        if self.MODE == "two player":
            if self._current_grid is not self._player2_grid \
                and self._player1_grid[self._current_row_i][0]["letter"] != "" \
                and self._player2_grid[self._current_row_i][0]["letter"] == "" :
                self._current_grid = self._player2_grid
            elif self._current_grid is not self._player1_grid \
                and self._player2_grid[self._current_row_i][0]["letter"] != "":
                self._current_row_i += 1 if self._current_row_i != self.N_ROWS - 1 else 0
                self._current_grid = self._player1_grid
        else:
            raise Exception("You called _switch_grid_check on a non-multiplayer game")

    def _create_grid(self):
        for i in range(self.N_ROWS):
            for j in range(self.N_LETTERS):
                x_padding_dist: int = j * self.DX
                y_padding_dist: int = i * self.DY
                square_width_dist: int = j * self.BOX_WIDTH
                square_height_dist: int = i * self.BOX_HEIGHT
                x: int = self._x + x_padding_dist + square_width_dist
                y: int = self._y + y_padding_dist + square_height_dist
                # save box coordinates
                self._current_grid[i][j]["x"] = x
                self._current_grid[i][j]["y"] = y
    
    def _draw_grid(self, grid: List[List[dict]]):
        for i in range(self.N_ROWS):
            for j in range(self.N_LETTERS):
                x: int = grid[i][j]["x"]
                y: int = grid[i][j]["y"]
                letter_box = pygame.Rect(x, y, 
                                         self.BOX_WIDTH,
                                         self.BOX_HEIGHT)
                pygame.draw.rect(self._screen, self.LIGHT_GREY, letter_box, width=2)

    def _create_two_player_wordle_grids(self): 
        # maintain current grid
        self._setup_grid_starting_x_y()
        self._create_grid()
        self._current_grid = self._player2_grid if self._current_grid is self._player1_grid else self._player2_grid
        self._setup_grid_starting_x_y()
        self._create_grid()
        self._current_grid = self._player1_grid if self._current_grid is self._player2_grid else self._player2_grid

    def _capture_main_keydown_event(self, event):
        if event.type == pygame.KEYDOWN:
            # attempt to erase letters
            if event.key == pygame.K_BACKSPACE and self._current_letter_i > 0: 
                self._current_guess: str = self._current_guess[:-1]
                self._current_letter_i -= 1
            # attempt to enter guess
            elif event.key == pygame.K_RETURN:
                self._process_current_guess()
            # process single letter input
            elif len(self._current_guess) < self.N_LETTERS and event.unicode.isalpha():
                self._current_guess += event.unicode.lower()
                self._current_letter_i += 1
            # process exit
            elif event.key == pygame.K_ESCAPE:
                pygame.quit() 
                sys.exit()

    def _process_current_guess(self):
        # correct number of letters
        if len(self._current_guess) == self.N_LETTERS and self._current_guess != "":
            # successful guess
            if self._current_guess in self.allowed_guesses_set:
                # save guess
                for letter_i, letter in enumerate(self._current_guess):
                    self._current_grid[self._current_row_i][letter_i]["letter"] = letter
                # reset next guess
                self._last_attempted_word = self._current_guess
                self._current_guess: str = ""
                self._player_letter_i: int = 0
                if self.MODE == "single player":
                    self._current_row_i += 1
            # invalid guess
            else:
                self._is_invalid_guess: bool = True
                self._timer_warning_flag: int = 0
        # incorrect number of lettters
        else:
            self._is_invalid_n_letters: bool = True
            self._timer_warning_flag: int = 0

    def _solo_game(self):
        game_is_running: bool = True
        self._setup_grid_starting_x_y()
        self._create_grid()
        while game_is_running:
            # background
            self._screen.fill(self.WHITE)
            self._draw_grid(self._current_grid)
            # title and underline
            self._draw_underlined_var_length_title()
            self._capture_player_events()
            self._update_game_text()
            self._render_current_guess_letters(self._current_grid)
            self._render_past_attempts(self._current_grid)
            self._check_game_state()
            pygame.display.update()
            self._clock.tick(self.FPS)

    def _check_game_state(self):
        player1_last_row_attempted = True if self._player1_grid[self.N_ROWS - 1][0]["letter"] != "" else False
        if self.MODE == "single player":
            if (self._last_attempted_word.lower() == self._answer)\
                or player1_last_row_attempted:
                self._game_over = True
        elif self.MODE == "two player":
            player2_last_row_attempted = True if self._player2_grid[self.N_ROWS - 1][0]["letter"] != "" else False
            all_rows_attempted = True if player1_last_row_attempted and player2_last_row_attempted else False
            if (self._last_attempted_word.lower() == self._answer)\
                or all_rows_attempted:
                self._game_over = True
        else:
            raise ValueError(f"MODE has an invalid value")

    def _render_current_guess_letters(self, grid: List[List[dict]]):
        guess_row_i = self._get_current_guess_grid_row_i(grid)
        for i, letter in enumerate(self._current_guess):
            letter_surface = self.general_text_font.render(letter.upper(), 
                                                           True, 
                                                           self.BLACK)
            letter_hor_padding = (self.BOX_WIDTH - letter_surface.get_bounding_rect().width)/2
            x = grid[guess_row_i][i]["x"] + letter_hor_padding
            # the letter height is not true to size, so we'll apply our own vertical padding
            y = grid[guess_row_i][i]["y"] + self.BOX_VERT_PAD
            self._screen.blit(letter_surface, (x, y))
    
    @staticmethod
    def _get_grid_row_word(grid_row: List[dict]) -> str:
        word = ""
        for i in range(len(grid_row)):
            word += grid_row[i]["letter"]
        return word

    def _get_current_guess_grid_row_i(self, grid: List[List[dict]]) -> int:
        for i in range(len(grid)):
            if grid[i][0]["letter"] == "" or i == self.N_ROWS - 1:
                return i
        raise ValueError("Empty grid")

    def _render_past_attempts(self, grid: List[List[dict]]):
        current_guess_row_i = self._get_current_guess_grid_row_i(grid)
        for row_n in range(0, current_guess_row_i + 1):
            row_guess = self._get_grid_row_word(grid[row_n])
            # letter colour check
            for letter_i, letter in enumerate(row_guess):
                x = grid[row_n][letter_i]["x"]
                y = grid[row_n][letter_i]["y"]
                color_box_rect = pygame.Rect((x, y), (self.BOX_WIDTH, self.BOX_HEIGHT))
                if char_is_green(row_guess, letter_i, self._answer):
                    pygame.draw.rect(self._screen, self.GREEN, color_box_rect)
                elif char_is_yellow(row_guess, letter_i, self._answer):
                    pygame.draw.rect(self._screen, self.YELLOW, color_box_rect)
                elif char_is_grey(row_guess, letter_i, self._answer):
                    pygame.draw.rect(self._screen, self.GREY, color_box_rect)
                else:
                    raise Exception(f"{row_guess[letter_i]} at index {letter_i} from {row_guess} did not get colored for the answer: {self._answer}")
                prev_surface = self.general_text_font.render(letter.upper(), True, self.WHITE)
                letter_hor_padding = (self.BOX_WIDTH - prev_surface.get_bounding_rect().width) / 2

                self._screen.blit(prev_surface, (x + letter_hor_padding, y + self.BOX_VERT_PAD))

    def _capture_player_events(self):
        for event in pygame.event.get():
            if self._game_over:
                self._capture_endgame_events(event)
            else:
                self._capture_main_keydown_event(event)

    def _capture_endgame_events(self, event):
        if event.type == pygame.KEYDOWN:
            # exit or replay on game over
            if event.key == pygame.K_RETURN and self.MODE == "singe player":
                self._define_new_game_attributes()
                self._solo_game()
            elif event.key == pygame.K_RETURN and self.MODE == "two player":
                self._define_new_game_attributes()
                self._two_player_game()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def _update_game_text(self):
        # invalid word warning
        if self._is_invalid_guess:
            text_surface = self.warning_text_font.render(self.invalid_word_str, 
                                                         True, 
                                                         self.RED)
            self._render_warning_text(text_surface)
            self._timer_warning_flag += 1
            self._is_invalid_n_letters = False
        # invalid number of letters warning
        elif self._is_invalid_n_letters:
            text_surface = self.warning_text_font.render(self.invalid_len_str, 
                                                         True, 
                                                         self.RED)
            self._render_warning_text(text_surface)
            self._timer_warning_flag += 1
            self._is_invalid_guess = False
        # reset flag and clear text
        if self._timer_warning_flag == self.TEXT_TIMER * self.FPS:
            self._is_invalid_guess = False
            self._is_invalid_n_letters = False
            self._timer_warning_flag = 0
        # game won text
        if self._game_over and self._last_attempted_word == self._answer:
            text_surface = self.warning_text_font.render(self.game_won_str, 
                                                         True, 
                                                         self.GREEN)
            self._render_game_over_text(text_surface)
        # game loss text
        elif self._game_over and self._last_attempted_word != self._answer:
            text_surface = self.warning_text_font.render(f'{self.game_loss_str1} "{self._answer}", ' + self.game_loss_str2, 
                                                         True, 
                                                         self.RED)
            self._render_game_over_text(text_surface)

    def _render_game_over_text(self, text_surface) -> None:
        # centered text
        text_x, *_ = text_surface.get_rect(center=(self.CENTER_X, self.CENTER_Y))
        # text below grid
        text_y = self._y + (self.DY * 7) + (self.BOX_HEIGHT * self.N_ROWS)
        self._screen.blit(text_surface, (text_x, text_y))

    def _load_words_txt_file(self) -> None:
        allowed_guesses_fp: str = path.join(self._data_dir_path, self._allowed_words_fname)
        possible_solutions_fp: str = path.join(self._data_dir_path, self._solution_words_fname)
        try: 
            with open(allowed_guesses_fp, mode="r", encoding="utf-8") as f:
                self.allowed_guesses_set: set = {word.lower() for word in f.read().split("\n") if len(word) == self.N_LETTERS}
            with open(possible_solutions_fp, mode="r", encoding="utf-8") as f:
                self.possible_solutions_set: set = {solution.lower() for solution in f.read().split("\n") if len(solution) == self.N_LETTERS}
            # verify solution file is a subset of superset guess file
            self._validate_word_sets()
        except Exception as e:
            print(f"Error: {e} loading word sets")
            sys.exit()

    def _validate_word_sets(self):
        if len(self.possible_solutions_set) == 0:
            raise ValueError(f"The list of possible solutions is empty")
        if len(self.allowed_guesses_set) == 0:
            raise ValueError(f"The list of allowed guesses is empty")
        if not self.possible_solutions_set.issubset(self.allowed_guesses_set):
            missing_allowed_guesses = self.possible_solutions_set - self.allowed_guesses_set
            raise ValueError(f"{missing_allowed_guesses} are solutions missing from allowed guesses")

    def _validate_player_settings(self, player_settings: dict) -> None:
        if self.MODE not in self.AVAILABLE_MODES:
            raise ValueError(f"{self.MODE} is not supported, you must use a mode in: {self.AVAILABLE_MODES}")
        if self.MIN_N_LETTERS > self.N_LETTERS > self.MAX_N_LETTERS:
            raise ValueError(f"given number of letters must be between {self.MIN_N_LETTERS}\
                               and {self.MAX_N_LETTERS}, you attempted to set it at {self.N_LETTERS}")
        if self.MIN_N_ROWS > self.N_ROWS > self.MAX_N_ROWS:
            raise ValueError(f"given number of rows must be between {self.MIN_N_ROWS}\
                               and {self.MAX_N_ROWS}, you attempted to set it at {self.N_ROWS}")
        if self.LANGUAGE not in self.AVAILABLE_LANGUAGES:
            raise ValueError(f"{self.LANGUAGE} is not supported, you must use a language in: {self.AVAILABLE_LANGUAGES}")
        if not Path(self._data_dir_path).is_dir():
            raise FileNotFoundError(f"No folder exists at {self._data_dir_path}")
        if not path.isfile(path.join(self._data_dir_path, self._allowed_words_fname)):
            raise FileNotFoundError(f"{self._allowed_words_fname} file does not exist in {self._data_dir_path}")
        if not path.isfile(path.join(self._data_dir_path, self._solution_words_fname)):
            raise FileNotFoundError(f"{self._solution_words_fname} file does not exist in {self._data_dir_path}")
        for k, _ in player_settings.items():
            if k not in self.PLAYER_VALID_KWARGS_KEYS:
                print(f"Warning: {k} is not a supported keyword for self,\
                        supported kwargs are {self.PLAYER_VALID_KWARGS_KEYS}")

    def _validate_kwargs(self, **kwargs) -> None:
        player_settings = {k.lower():v for k,v in kwargs.items()}
        self.MODE: str = player_settings.get("mode", "single player").lower()
        self.N_LETTERS: int = int(player_settings.get("letters", self.BASE_N_LETTERS))
        self.N_ROWS: int = int(player_settings.get("rows", self.BASE_N_ROWS))
        self.LANGUAGE: str = player_settings.get("language", "english").lower()
        self._data_dir_path: str = player_settings.get("text_directory_path", None)
        self._allowed_words_fname: str = player_settings.get("allowed_guesses_file_name", None)
        self._solution_words_fname: str = player_settings.get("possible_solutions_file_name", None)
        self._setup_missing_inputs()
        self._validate_player_settings(player_settings)
        self._load_words_txt_file()
        self._validate_word_sets()

    def _setup_missing_inputs(self):
        if self._data_dir_path is None:
            self._data_dir_path = path.join(getcwd(), "data")
        if self._allowed_words_fname is None:
            if self.LANGUAGE == "english": 
                self._allowed_words_fname = "en_allowed_guesses.txt"
            elif self.LANGUAGE == "français":
                self._allowed_words_fname = "fr_allowed_guesses.txt"
        if self._solution_words_fname is None:
            if self.LANGUAGE == "english":
                self._solution_words_fname = "en_answer_words.txt"
            elif self.LANGUAGE == "français":
                self._solution_words_fname = "fr_answer_words.txt"

        # tack on text file extension if necessary
        for fname in [self._allowed_words_fname, self._solution_words_fname]:
            if len(fname) > 4 and fname[-4:] != ".txt":
                fname = fname + ".txt"

    def _setup_grid_starting_x_y(self):
        # starting (x, y) drawing positions for letter boxes - we want the grid center stage
        self._y = self.CENTER_Y - (self.TOTAL_GRID_HEIGHT / 2)
        if self.MODE == "single player":
            self._x = self.CENTER_X - (self.TOTAL_GRID_WIDTH / 2)
        elif self.MODE == "two player" and self._current_grid is self._player1_grid:
            self._x = self.CENTER_X - self.TOTAL_GRID_WIDTH - (self.DX * 2)
        elif self.MODE == "two player" and self._current_grid is self._player2_grid:
            self._x = self.CENTER_X + (self.DX * 2)
        else:
            raise ValueError("Incorrect coord setup starting point due to current_grid misalignment or incorrect mode")

    def _setup_display_attributes(self):
        original_width, original_height = 1368, 912 
        display_info = pygame.display.Info()
        self.DISPLAY_WIDTH = display_info.current_w
        self.DISPLAY_HEIGHT = display_info.current_h
        self.scale_x = self.DISPLAY_WIDTH / original_width
        self.scale_y = self.DISPLAY_HEIGHT / original_height
        self.DX: int = int(10/self.scale_x)
        self.DY: int = int(10/self.scale_y)
        self.BOX_WIDTH: int = int(50/self.scale_x)
        self.BOX_HEIGHT: int = int(50/self.scale_y)
        self.BOX_HOR_PAD: int = int(10/self.scale_x)
        self.BOX_VERT_PAD: int = int(5/self.scale_y) 
        self.CENTER_X = self.DISPLAY_WIDTH / 2
        self.CENTER_Y = self.DISPLAY_HEIGHT / 2 
        self.TOTAL_GRID_HEIGHT = self.N_ROWS * (self.BOX_HEIGHT + self.DY)
        self.TOTAL_GRID_WIDTH = self.N_LETTERS * (self.BOX_WIDTH + self.DX) 
        self._screen = pygame.display.set_mode((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        self.general_text_font = pygame.font.Font(None, int(65 / (self.scale_x * self.scale_y)))
        self.warning_text_font = pygame.font.Font(None, int(40 / (self.scale_x * self.scale_y)))

    def _define_new_game_attributes(self):
        letter_schema: dict = {"x":None, "y":None, "letter":""}
        row_schema: List[dict] = [letter_schema.copy() for _ in range(self.N_LETTERS)]
        grid_schema: List[List[dict]] = [deepcopy(row_schema) for _ in range(self.N_ROWS)]
        self._clock = pygame.time.Clock()
        self._last_attempted_word: str = ""
        self._current_guess = ""
        self._current_letter_i: int = 0
        self._answer: str = random.choice(list(self.possible_solutions_set))
        self._game_over: bool = False
        self._is_invalid_guess: bool = False
        self._is_invalid_n_letters: bool = False
        self._timer_warning_flag: int = 0
        self._player1_grid: List[List[dict]] = deepcopy(grid_schema)
        if self.MODE == "two player":
            self._player2_grid: List[List[dict]] = deepcopy(grid_schema)
            self._blocked_box_i: int = random.choice(range(0,self.N_LETTERS))
        self._current_grid: List[List[tuple]] = self._player1_grid
        self._current_row_i: int = 0

    def _draw_underlined_var_length_title(self) -> None:
        # draw a variable length title with a line underneath
        title = self.general_text_font.render(self.title, True, self.BLACK)
        title_x, _, title_width, title_height = title.get_rect(center=(self.CENTER_X, self.CENTER_Y))
        self._draw_title_line(title_x, title_width)
        # render title above the underline
        title_y = self.CENTER_Y - (self.TOTAL_GRID_HEIGHT / 2) - (self.BOX_HEIGHT * 1.5) - (title_height/2)
        title_start_pos = (title_x, title_y)
        self._screen.blit(title, title_start_pos)

    def _draw_title_line(self, title_x: int, title_width: int) -> None:
        # beginning from the first letter box (our starting position)
        # - move x left by 5 pixels
        # - move y up by a single box height
        start_line_x = title_x - 5
        line_y = self.CENTER_Y - (self.TOTAL_GRID_HEIGHT / 2) - self.BOX_HEIGHT
        # end of line is at the opposite end
        end_line_x = title_x + title_width + 5

        line_start_pos = (start_line_x, line_y)
        line_end_pos = (end_line_x, line_y)

        pygame.draw.line(surface=self._screen,
                         color=self.DARK_GREY,
                         start_pos=line_start_pos,
                         end_pos=line_end_pos,
                         width=1)

    def _render_warning_text(self, text_surface: pygame.Surface) -> None:
        # centered text
        text_x, *_ = text_surface.get_rect(center=(self.CENTER_X, self.CENTER_Y))
        # text above between title and grid
        text_y = self._y - (self.DY * 4)
        self._screen.blit(text_surface, (text_x, text_y))

if __name__ == "__main__":
    WordleUI(**dict(arg.split('=') for arg in sys.argv[1:]))