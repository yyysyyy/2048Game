import tkinter as tk

import messagebox

from a3_support import *

# Write your classes here
class Model:
    def __init__(self) -> None:
        self.new_game()         
    
    def new_game(self) -> None:
        self.tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self.score = 0
        self.undo = 3
        self.add_tile()
        self.add_tile()
        self.undos = []
        self.scores = []
        self.game_over = False
        self.game_won = False

    def get_tiles(self) -> list[list[Optional[int]]]:
        return self.tiles
    
    def add_tile(self) -> None:
        t = generate_tile(self.tiles)
        #print(t)
        self.tiles[t[0][0]][t[0][1]] = t[1]
    
    def move_left(self) -> None:
        self.tiles = stack_left(self.tiles)
        self.tiles, score_added = combine_left(self.tiles)
        self.tiles = stack_left(self.tiles)
        self.score += score_added
        #self.add_tile()
    
    def move_right(self) -> None:
        self.tiles = reverse(self.tiles)
        self.move_left()
        self.tiles = reverse(self.tiles)
    
    def move_up(self) -> None:
        self.tiles = transpose(self.tiles)
        self.move_left()
        self.tiles = transpose(self.tiles)
    
    def move_down(self) -> None:
        self.tiles = transpose(self.tiles)
        self.move_right()
        self.tiles = transpose(self.tiles)
    
    def attempt_move(self,move: str) -> bool:
        if self.game_over:
            return False
        self.undos.append(self.tiles)
        self.undos.append(self.score)
        if move == LEFT:
            self.move_left()
            self.add_tile()
        elif move == RIGHT:
            self.move_right()
            self.add_tile()
        elif move == UP:
            self.move_up()
            self.add_tile()
        elif move == DOWN:
            self.move_down()
            self.add_tile()
        if self.has_lost():
            self.game_over = True
            return True
        if self.has_won():
            self.game_won = True
            return True
        return False

    def has_won(self) -> bool:
        for row in self.tiles:
            for tile in row:
                if tile == 2048:
                    return True
        return False
    
    def has_lost(self) -> bool:
        for row in self.tiles:
            for tile in row:
                if tile is None:
                    return False
        return True
    
    def get_score(self) -> int:
        return self.score
    
    def get_undos_remaining(self) -> int:
        return self.undo
    
    def use_undo(self) -> None:
        if self.undo == 0:
            return
        if len(self.undos) == 0:
            return
        self.undo -= 1
        self.tiles = self.undos.pop()
        self.score = self.scores.pop()

class GameGrid(tk.Canvas):
    def __init__(self,master:tk.Tk,**kwargs) -> None:
        super().__init__(master,width=400,height=400,**kwargs,bg='#d9d9d9')
        self.grid(row=1,column=0)
        self.label = tk.Label(self.master,text="2048",bg="#FFD700",fg="white",font=TITLE_FONT,height=1,width=10)
        self.label.grid(row=0,column=0)

    def _get_bbox(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
        x,y = position
        x_min = x*100 + 10
        y_min = y*100 + 10
        x_max = x_min + 90
        y_max = y_min + 90
        return (x_min,y_min,x_max,y_max)

    def _get_midpoint(self,position:tuple[int,int]) ->tuple[int,int]:
        x,y = position
        x_mid = x*100 + 50
        y_mid = y*100 + 50
        return (x_mid,y_mid)

    def clear(self) -> None:
        self.delete(tk.ALL)

    def redraw(self,tiles: list[list[Optional[int]]]) -> None:
        self.clear()
        #self.create_rectangle(0,0,400,400,outline=BACKGROUND_COLOUR,width=5)
        self.create_rectangle(0,0,400,400,fill=BACKGROUND_COLOUR,outline='#d9d9d9')
        for row in range(len(tiles)):
            for col in range(len(tiles[row])):
                if tiles[row][col] is not None:
                    self.create_rectangle(self._get_bbox((col,row)),fill=COLOURS[tiles[row][col]],outline=COLOURS[tiles[row][col]])
                    self.create_text(self._get_midpoint((col,row)),text=str(tiles[row][col]),fill=FG_COLOURS[tiles[row][col]],font=TILE_FONT)
                else:
                    self.create_rectangle(self._get_bbox((col,row)),fill=COLOURS[None],outline=BACKGROUND_COLOUR)   
        

class Game:
    def __init__(self,master:tk.Tk) -> None:
        self.master = master
        self.model = Model()
        self.view = GameGrid(self.master)
        self.statusBar = StatusBar(self.master)
        self.master.title("CSSE1001/7030 2022 Semester 2 A3")
        self.master.resizable(False,False)
        self.master.bind("<Key>",self.attempt_move)
        self.view.create_text(70,470,text=str(self.model.score),font= ('Arial bold', 20),fill='white')
        self.view.create_text(200,470,text=str(self.model.undo),font=('Arial bold', 20),fill='white')
        self.view.redraw(self.model.get_tiles())
        self.statusBar.set_callbacks(self.start_new_game,self.undo_previous_move)
        
    def draw(self) -> None:
        if self.model.game_won:
            messagebox.showinfo(title=WIN_MESSAGE,message=WIN_MESSAGE)
            return
        self.view.redraw(self.model.get_tiles())
        self.statusBar.redraw_infos(self.model.get_score(),self.model.get_undos_remaining())
        if self.model.game_over:
            messagebox.showinfo(title=LOSS_MESSAGE,message=LOSS_MESSAGE)   
            return
    
    def attempt_move(self,event:tk.Event) -> None:
        if self.model.game_over or self.model.game_won:
            return 
        self.model.attempt_move(event.char)
        self.draw()
    
    def new_tile(self) -> None:
        self.model.add_tile()
        self.draw()
    
    def undo_previous_move(self) -> None:
        self.model.use_undo()
        self.draw()
        self.statusBar.redraw_infos(self.model.get_score(),self.model.get_undos_remaining())

    def start_new_game(self) ->None:
        self.model = Model()
        self.draw()
        self.statusBar.redraw_infos(self.model.get_score(),self.model.get_undos_remaining())

class StatusBar(tk.Frame):
    def __init__(self,master:tk.Tk,**kwargs):
        super().__init__(master,**kwargs)
        self.grid(row=2,column=0)

        self.score = tk.Label(self,text="SCORE",bg=BACKGROUND_COLOUR,fg=COLOURS[None],font=('Arial bold', 20),height=1,width=6)
        self.score.grid(row=0,column=0)
        self.scores = tk.Label(self,text="0",bg=BACKGROUND_COLOUR,fg="white",font=('Arial bold', 20),height=1,width=6)
        self.scores.grid(row=1,column=0)

        

        self.undo = tk.Label(self,text="UNDOS",bg=BACKGROUND_COLOUR,fg=COLOURS[None],font=('Arial bold', 20),height=1,width=6)
        self.undo.grid(row=0,column=2)
        self.undos = tk.Label(self,text="3",bg=BACKGROUND_COLOUR,fg="white",font=('Arial bold', 20),height=1,width=6)
        self.undos.grid(row=1,column=2)

        

        self.restart_button = tk.Button(self,text="New Game",font=('Arial bold', 10),fg='black',height=1,width=9,bg='#d9d9d9')
        self.restart_button.grid(row=0,column=4)
        self.undo_button = tk.Button(self,text="Undo Move",font=('Arial bold', 10),fg='black',height=1,width=9,bg='#d9d9d9')
        self.undo_button.grid(row=1,column=4)
    
    def redraw_infos(self,score:int,undos:int) -> None:
        self.scores.config(text=score)
        self.undos.config(text=undos)
    
    def set_callbacks(self,new_game_command:callable,undo_command:callable) -> None:
        self.restart_button.config(command=new_game_command)
        self.undo_button.config(command=undo_command)

def play_game(root):
    game = Game(root)

if __name__ == '__main__':
    root = tk.Tk()
    play_game(root)
    root.mainloop()
