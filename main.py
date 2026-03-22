import pyxel
import random

GRID = 8
CELL = 16

PIECES = [
    [(0,0)],
    [(0,0),(1,0)],
    [(0,0),(0,1)],
    [(0,0),(1,0),(2,0)],
    [(0,0),(0,1),(0,2)],
    [(0,0),(1,0),(0,1)],
    [(0,0),(1,0),(2,0),(3,0)],
    [(0,0),(0,1),(0,2),(0,3)],
    [(0,0),(1,0),(0,1),(1,1)],
    [(0,0),(0,1),(0,2),(1,2)],
    [(0,1),(1,0),(1,1),(2,1)],
    [(0,0),(1,0),(1,1),(2,1)],
]

PIECE_COLORS = {
    0: 8, 1: 11, 2: 11, 3: 10, 4: 10, 5: 9,
    6: 12, 7: 12, 8: 14, 9: 2, 10: 3, 11: 5,
}

class App:
    def __init__(self):
        pyxel.init(GRID * CELL, GRID * CELL + 40, title="Mini BlockBlast")
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.grid = [[0] * GRID for _ in range(GRID)]
        self.cursor = [0, 0]
        self.pieces = [random.randrange(len(PIECES)) for _ in range(3)]
        self.last_pieces = self.pieces[:]
        self.used = [False, False, False]
        self.selected = 0
        self.score = 0
        self.combo = 0
        self.gameover = False
        self.clear_anim = []

    def new_pieces(self):
        new_list = []
        for _ in range(3):
            idx = random.randrange(len(PIECES))
            while idx in self.last_pieces:
                idx = random.randrange(len(PIECES))
            new_list.append(idx)
        self.pieces = new_list
        self.used = [False, False, False]
        self.last_pieces = new_list[:]
        # 新しいピースが来たらすぐにゲームオーバー判定
        self.check_gameover()

    def can_place(self, gx, gy, piece):
        for dx, dy in piece:
            x = gx + dx
            y = gy + dy
            if not (0 <= x < GRID and 0 <= y < GRID):
                return False
            if self.grid[y][x] == 1:
                return False
        return True

    def can_place_anywhere(self, piece):
        for y in range(GRID):
            for x in range(GRID):
                if self.can_place(x, y, piece):
                    return True
        return False

    def place(self, gx, gy, piece):
        for dx, dy in piece:
            self.grid[gy + dy][gx + dx] = 1

    def clear_lines(self):
        cleared = 0
        # 横一列
        for y in range(GRID):
            if all(self.grid[y][x] == 1 for x in range(GRID)):
                for x in range(GRID):
                    self.grid[y][x] = 0
                cleared += 1
        # 縦一列
        for x in range(GRID):
            if all(self.grid[y][x] == 1 for y in range(GRID)):
                for y in range(GRID):
                    self.grid[y][x] = 0
                cleared += 1
        return cleared

    def piece_size(self, piece):
        max_x = max(dx for dx, dy in piece)
        max_y = max(dy for dx, dy in piece)
        return max_x + 1, max_y + 1

    def check_gameover(self):
        """現在の3つのピースのうち1つでも置ける場所があればゲーム続行。
           どれも置けなければ gameover をセットして消去アニメを準備する。"""
        for idx in range(3):
            if self.used[idx]:
                continue
            piece_index = self.pieces[idx]
            piece = PIECES[piece_index]
            if self.can_place_anywhere(piece):
                return False
        # ここに来たらどの未使用ピースも置けない
        self.gameover = True
        self.clear_anim = [(x, y) for y in range(GRID) for x in range(GRID) if self.grid[y][x] == 1]
        random.shuffle(self.clear_anim)
        return True

    def update(self):
        # ゲームオーバー中の処理（Rでリセット、消去アニメのみ進行）
        if self.gameover:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
                return
            if self.clear_anim:
                x, y = self.clear_anim.pop()
                self.grid[y][x] = 0
            return

        # 毎フレーム開始時にも念のため判定（初期状態や外部で盤面が変わった場合に対応）
        self.check_gameover()
        if self.gameover:
            return

        piece_index = self.pieces[self.selected]
        piece = PIECES[piece_index]
        w, h = self.piece_size(piece)

        # カーソル移動（ピースのサイズを考慮）
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.cursor[0] = max(0, self.cursor[0] - 1)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.cursor[0] = min(GRID - w, self.cursor[0] + 1)
        if pyxel.btnp(pyxel.KEY_UP):
            self.cursor[1] = max(0, self.cursor[1] - 1)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.cursor[1] = min(GRID - h, self.cursor[1] + 1)

        # ピース選択
        if pyxel.btnp(pyxel.KEY_1) and not self.used[0]:
            self.selected = 0
        if pyxel.btnp(pyxel.KEY_2) and not self.used[1]:
            self.selected = 1
        if pyxel.btnp(pyxel.KEY_3) and not self.used[2]:
            self.selected = 2

        # Zキーで配置
        if pyxel.btnp(pyxel.KEY_Z):
            idx = self.selected
            if not self.used[idx]:
                piece_index = self.pieces[idx]
                piece = PIECES[piece_index]
                x, y = self.cursor
                if self.can_place(x, y, piece):
                    self.place(x, y, piece)
                    cleared = self.clear_lines()
                    self.score += len(piece)
                    if cleared > 0:
                        self.combo += 1
                        self.score += cleared * 10 * self.combo
                    else:
                        self.combo = 0
                    self.used[idx] = True
                    # 未使用のピースに選択を移す
                    for i in range(3):
                        if not self.used[i]:
                            self.selected = i
                            break

            # 全部使ったら新しいピースを配る（配った直後にゲームオーバー判定）
            if all(self.used):
                self.new_pieces()

            # ピースを置いた後にも判定（置いた結果で置けなくなる場合がある）
            self.check_gameover()

    def draw(self):
        pyxel.cls(0)
        # 盤面描画
        for y in range(GRID):
            for x in range(GRID):
                col = 7 if self.grid[y][x] else 1
                pyxel.rect(x * CELL, y * CELL, CELL - 1, CELL - 1, col)

        # カーソル
        cx, cy = self.cursor
        pyxel.rectb(cx * CELL, cy * CELL, CELL - 1, CELL - 1, 10)

        # 選択中ピースの表示（ゴースト表示含む）
        piece_index = self.pieces[self.selected]
        piece = PIECES[piece_index]
        can = self.can_place(cx, cy, piece)
        normal_col = PIECE_COLORS[piece_index]
        ghost_col = 8
        for dx, dy in piece:
            px = (cx + dx) * CELL
            py = (cy + dy) * CELL
            if can:
                pyxel.rect(px, py, CELL - 1, CELL - 1, normal_col)
            else:
                pyxel.rectb(px, py, CELL - 1, CELL - 1, ghost_col)

        # ピース一覧
        self.draw_pieces()

        # スコア表示
        pyxel.text(2, 2, f"SCORE: {self.score}", 3)
        pyxel.text(2, 10, f"COMBO: {self.combo}", 10)

        # ゲームオーバー表示
        if self.gameover:
            cx = (GRID * CELL) // 2
            cy = (GRID * CELL) // 2
            pyxel.text(cx - 20, cy - 10, "GAME OVER", 8)
            pyxel.text(cx - 32, cy + 2, "PRESS R TO RETRY", 10)

    def draw_pieces(self):
        y = GRID * CELL + 2
        for i, piece_index in enumerate(self.pieces):
            if self.used[i]:
                continue
            x = 10 + i * 40
            piece = PIECES[piece_index]
            col = PIECE_COLORS[piece_index]
            pyxel.text(x, y, f"{i+1}:", 7)
            for dx, dy in piece:
                px = x + dx * 4
                py = y + 10 + dy * 4
                pyxel.rect(px, py, 3, 3, col)

App()