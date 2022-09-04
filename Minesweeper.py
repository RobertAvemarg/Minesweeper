import os
import csv
import random
import time

import tkinter
import tkinter.messagebox
import tkinter.simpledialog


MAX_MINES = 800
MAX_XY_DIMENSIONS = 30

COLORS = [	'#FFFFFF',
			'#0000FF',
			'#008200',
			'#FF0000',
			'#000084',
			'#840000',
			'#008284',
			'#840084',
			'#000000']

MODE = {"easy" : "easy",
		"medium" : "medium",
		"hard" : "hard",
		"custom" : "custom"}



class GUI():
	def __init__(self):
		self.buttonArray = []

		self.mode = MODE["easy"]
		self.gameover = False
		self.game = None
		self.rows = 8
		self.cols = 8

		self.numMines = 10
		self.numMarkedFields = 0


	def initGUI(self):
		self.window = tkinter.Tk()
		self.window.title("Minesweeper")


	def createMenu(self):
		menubar = tkinter.Menu(self.window)

		menusize = tkinter.Menu(self.window, tearoff=0)
		menusize.add_command(label = "easy (8x8 with 10 mines)", command = lambda: self.setGameParametersAndRestart(8, 8, 10, MODE["easy"]))
		menusize.add_command(label = "medium (16x16 with 40 mines)", command = lambda: self.setGameParametersAndRestart(16, 16, 40, MODE["medium"]))
		menusize.add_command(label = "hard (30x16 with 99 mines)", command = lambda: self.setGameParametersAndRestart(30, 16, 99, MODE["hard"]))
		menusize.add_command(label = "custom", command = self.setCustomSize)

		menubar.add_cascade(label = "Difficulty", menu = menusize)

		menubar.add_command(label = "Leaderboard", command = lambda: self.showHighscore())

		menubar.add_command(label = "Close", command=lambda: self.window.destroy())
		self.window.config(menu = menubar)


	def setCustomSize(self):
		rows, cols, numMines = self.askCustomParameters()
		self.setGameParametersAndRestart(rows, cols, numMines, 4)


	def askCustomParameters(self):
		rows = tkinter.simpledialog.askinteger("custom", "Please enter number of lines", initialvalue=5)
		cols = tkinter.simpledialog.askinteger("custom", "Please enter number of columns", initialvalue=5)
		numMines = tkinter.simpledialog.askinteger("custom", "Please enter number of mines", initialvalue=5)

		return self.askAgainIfNotValid(rows, cols, numMines)


	def askAgainIfNotValid(self, rows, cols, numMines):
		while rows > MAX_XY_DIMENSIONS:
			rows = tkinter.simpledialog.askinteger("custom", "The maximum number of lines is " + MAX_XY_DIMENSIONS + "\nPlease enter number of lines")

		while cols > MAX_XY_DIMENSIONS:
			cols = tkinter.simpledialog.askinteger("custom", "The maximum number of columns is " + MAX_XY_DIMENSIONS + "\nPlease enter number of columns")

		while numMines > MAX_MINES:
			numMines = tkinter.simpledialog.askinteger("custom", "The maximum number of mines is " + MAX_MINES + "\nPlease enter number of mines")

		if rows < 5 or cols < 5:
			tkinter.messagebox.showinfo("Minimum size", "The field must be at least 5x5 squares.")
			self.setCustomSize()

		while numMines > rows * cols:
			numMines = tkinter.simpledialog.askinteger("custom", "The maximum number of mines for this size is: " + str(rows * cols) + "\nPlease enter number of mines")

		return rows, cols, numMines


	def setGameParametersAndRestart(self, rows, cols, numMines, mode):
		self.rows = rows
		self.cols = cols
		self.numMines = numMines
		self.mode = mode
		self.restartGame()


	def createGUI(self):
		self.mineLabel = tkinter.Label(self.window, text="Mines:", height = 1).grid(row = 0, column = 0,columnspan= 2)
		self.mineCountLabel = tkinter.Label(self.window,text=str(self.numMines))
		self.mineCountLabel.grid(row =0, column = self.cols-2 , columnspan= 2)

		self.time = tkinter.Label(self.window, text="Time:").grid(rows = 1, column = 0,columnspan= 2)
		self.timestamp = tkinter.Label(self.window,text="0")
		self.timestamp.grid(row = 1, column = self.cols-2 , columnspan = 2)

		tkinter.Button(self.window, text = "Restart", command = self.restartGame).grid(row = 3, column = 0, columnspan = self.cols, sticky = tkinter.N + tkinter.W + tkinter.S + tkinter.E)

		self.createButtonGrid()

		self.button_color = self.buttonArray[0][0].cget("background")

		self.createGame()
		self.game.start()


	def createButtonGrid(self):
		for x in range(0, self.rows):
			self.buttonArray.append([])
			for y in range(0, self.cols):
				# bind actions
				b = tkinter.Button(self.window, text = " ", width = 2, command = lambda x = x, y = y: self.leftClick(x, y))
				b.bind("<Button-3>", lambda e, x = x, y = y: self.rightClick(x, y))

				# add button to grid
				b.grid(row = x+4, column = y, sticky = tkinter.N + tkinter.W + tkinter.S + tkinter.E)
				b["font"] = ('Helvetica', 10, 'bold')
				self.buttonArray[x].append(b)


	def createGame(self):
		self.game = Game(self.rows, self.cols, self.numMines)


	def restartGame(self):
		self.buttonArray = []
		self.numMarkedFields = 0
		self.gameover = False
		self.window.destroy()
		self.initGUI()
		self.createMenu()
		self.createGUI()
		self.game.start()


	def leftClick(self, x, y):
		if self.gameover:
			return

		if self.game.wasFirstClick():
			self.game.startingTime()
			self.tick()

		self.buttonArray[x][y].config(bg = self.button_color)

		foundMine = self.game.revealTile(x, y)
		self.update()

		if foundMine:
			self.gameover = True
			time = self.game.stop()
			self.update()
			tkinter.messagebox.showinfo("Gave Over", "You have lost.\nYour time: {:5.2f}s".format(time))

		if self.game.hasWon():
			self.gameover = True
			time = self.game.stop()
			self.update()
			tkinter.messagebox.showinfo("Gave Over", "You have won.\nYour time: {:5.2f}s".format(time))

			self.saveLeaderboard(time)


	def rightClick(self, x, y):
		if self.game.wasFirstClick():
			self.game.startingTime()
			self.tick()

		if self.game.isTileRevealed(x, y):
			return

		self.buttonArray[x][y].config(bg = self.button_color)
		self.game.markTile(x, y)
		marker = self.game.getMarker(x, y)

		if marker == 0:
			self.buttonArray[x][y]["text"] = " "
			self.buttonArray[x][y]['state'] = 'normal'
		if marker == 1:
			self.buttonArray[x][y]["text"] = "⚐"
			self.buttonArray[x][y]['state'] = 'disabled'
			self.numMarkedFields += 1
			self.mineCountLabel['text'] = str(self.numMines - self.numMarkedFields)
		if marker == 2:
			self.buttonArray[x][y]["text"] = "?"
			self.buttonArray[x][y]['state'] = 'disabled'
			self.numMarkedFields -= 1
			self.mineCountLabel['text'] = str(self.numMines - self.numMarkedFields)


	def update(self):
		for x in range(self.rows):
			for y in range(self.cols):
				if self.game.isTileRevealed(x, y):
					if self.game.isMine(x, y):
						self.buttonArray[x][y].config(background = 'red', disabledforeground = 'black', text = "*", state = "disabled")
					elif self.game.getNumNeighboringMines(x, y) > 0:
						self.buttonArray[x][y].config(disabledforeground = COLORS[self.game.getNumNeighboringMines(x, y)], text = str(self.game.getNumNeighboringMines(x, y)), state = "disabled")
					else:
						self.buttonArray[x][y].config(disabledforeground = COLORS[self.game.getNumNeighboringMines(x, y)])
						self.buttonArray[x][y].config(relief = tkinter.SUNKEN, state = "disabled")


	def tick(self):
		"""
		Updating the time display
		after(1000) waits 1s and calls the method again
		set to 500 because it sometimes lags
		"""
		if self.gameover:
			return

		seconds = int(time.time() - self.game.startTime)
		self.timestamp.configure(text = seconds)
		self.window.after(500, self.tick)


	def showHighscore(self):
		leaderboard = self.leaderBoardToString(self.readLeaderboard())
		tkinter.messagebox.showinfo("leaderboard", leaderboard)


	def readLeaderboard(self):
		leaderboard = []

		try:
			with open('leaderboard.txt', "r") as csv_file:
				csvReader = csv.reader(csv_file, delimiter=',')
				for row in csvReader:
					leaderboard.append(row)
				csv_file.close()
		except Exception as e:
			# file not found
			print(e)
			files = [f for f in os.listdir('.') if os.path.isfile(f)]
			print(files)
			leaderboard = ["Leaderboard does not yet exist"]

		return leaderboard


	def leaderBoardToString(self, leaderboard):
		l = ""
		for line in leaderboard:
			l += " ".join(line) + "\n"
		return l


	def saveLeaderboard(self, gameTime):
		leaderboard = self.readLeaderboard()

		leaderboardEasy = []
		leaderboardMedium = []
		leaderboardHard = []

		for line in leaderboard:
			if line[0] == MODE["easy"]:
				leaderboardEasy.append(line)
			if line[0] == MODE["medium"]:
				leaderboardMedium.append(line)
			if line[0] == MODE["hard"]:
				leaderboardHard.append(line)

		gameTime = round(gameTime, 2)

		if self.mode == MODE["easy"]: self.checkNewHighscore(leaderboardEasy, "easy", gameTime)
		if self.mode == MODE["medium"]: self.checkNewHighscore(leaderboardMedium, "medium", gameTime)
		if self.mode == MODE["hard"]: self.checkNewHighscore(leaderboardHard, "hard", gameTime)

		leaderboardEasy.sort(key=lambda x: float(x[5]))
		leaderboardMedium.sort(key=lambda x: float(x[5]))
		leaderboardHard.sort(key=lambda x: float(x[5]))

		print(leaderboardEasy)


		# it is easier to rewrite the leaderboard every time
		with open('leaderboard.txt', mode='w', newline='\n') as csvFile:
			csvWriter = csv.writer(csvFile, delimiter=',')
			for item in leaderboardEasy:
				csvWriter.writerow(item)
			for item in leaderboardMedium:
				csvWriter.writerow(item)
			for item in leaderboardHard:
				csvWriter.writerow(item)
			csvFile.close()


	def checkNewHighscore(self, leaderboard, mode, gameTime):
		times = [row[5] for row in leaderboard]
		if any(gameTime < float(i) for i in times) or len(leaderboard) < 5:
			name = tkinter.simpledialog.askstring("New high score", "Please enter name.")
			leaderboard.append([mode, str(self.rows), str(self.cols), str(self.numMines), name, str(gameTime), " s"])


	def sortTime(self, elem):
		return(float(elem.split(" ")[5]))



class Game():
	def __init__(self, rows, cols, numMines):
		self.startTime = 0
		self.endTime = 0
		self.field = Field(rows, cols, numMines)


	def start(self):
		self.field.prepare()


	def startingTime(self):
		self.startTime = time.time()


	def stop(self):
		self.endTime = time.time()
		self.field.reveal()
		return(self.endTime - self.startTime)


	def hasWon(self):
		return self.field.hasWon()


	def wasFirstClick(self):
		return self.field.wasFirstClick()


	def revealTile(self, x, y):
		return self.field.revealTileAndCheckMine(x, y)


	def isTileRevealed(self, x, y):
		return self.field.isTileRevealed(x, y)


	def markTile(self, x, y):
		self.field.markTile(x, y)


	def getMarker(self, x, y):
		return self.field.getMarker(x, y)


	def isMine(self, x, y):
		return self.field.isMine(x, y)


	def getNumNeighboringMines(self, x, y):
		return self.field.getNumNeighboringMines(x, y)



class Field():
	def __init__(self, rows, cols, numMines):
		self.rows = rows
		self.cols = cols
		self.numMines = numMines
		self.tileArray = []
		self.firstClick = True # first click is always save. mines get generated afterwards


	def prepare(self):
		self.tileArray = [[Tile() for col in range(self.cols)] for row in range(self.rows)]


	def placeMines(self, xClicked, yClicked):
		coordinates = [(x,y) for x in range(self.rows) for y in range(self.cols)]
		coordinates.remove((xClicked, yClicked))

		for mine in range(self.numMines):
			coordinate = random.choice(coordinates)
			x = coordinate[0]
			y = coordinate[1]

			self.tileArray[x][y].placeMine()
			coordinates.remove((x,y))

			self.updateNeighborhood(x, y)


	def updateNeighborhood(self, x, y):
		for xDirection in range(-1,2):
			for yDirection in range(-1,2):
				if self.inBounds(x + xDirection, y + yDirection):
					self.tileArray[x + xDirection][y + yDirection].increaseNeighboringMines()


	def reveal(self):
		for x in range(self.rows):
			for y in range(self.cols):
				self.tileArray[x][y].reveal()


	def revealTileAndCheckMine(self, x, y):
		"""
		return: True if a mine was hit otherwise False
		"""
		if self.tileArray[x][y].marker == 0 and self.tileArray[x][y].revealed == False:

			# check if it was the first click and the mines need to be placed
			if self.firstClick:
				self.placeMines(x, y)
				self.firstClick = False

			self.revealEmptyTiles(x, y)
			self.tileArray[x][y].reveal()

			return self.isMine(x, y)

		return False


	def revealEmptyTiles(self, x, y): # TODO kann kaputt gegangen sein
		if self.tileArray[x][y].revealed or self.tileArray[x][y].marker != 0:
			return

		self.tileArray[x][y].reveal()

		if self.getNumNeighboringMines(x, y) == 0:
			for xDirection in range(-1,2):
				for yDirection in range(-1,2):
					if xDirection == 0 and yDirection == 0:
						continue
					if self.inBounds(x + xDirection, y + yDirection):
						self.revealEmptyTiles(x + xDirection, y + yDirection)


	def inBounds(self, x, y):
		if x >= 0 and x < self.rows and y >= 0 and y < self.cols:
			return True
		return False


	def hasWon(self):
		"""
		Checks whether the game has been won by comparing the number of hidden squares with the number of mines.
		"""
		numHiddenTiles = 0

		for x in range(self.rows):
			for y in range(self.cols):
				if not self.isTileRevealed(x, y):
					numHiddenTiles +=1

		if numHiddenTiles == self.numMines:
			return True
		else:
			return False


	def wasFirstClick(self):
		return self.firstClick


	def isTileRevealed(self, x, y):
		return self.tileArray[x][y].isRevealed()

	def markTile(self, x, y):
		if self.tileArray[x][y].revealed == False:
			self.tileArray[x][y].setNextMarker()


	def getMarker(self, x, y):
		return self.tileArray[x][y].getMarker()


	def isMine(self, x, y):
		return self.tileArray[x][y].isMine()


	def getNumNeighboringMines(self, x, y):
		return self.tileArray[x][y].getNumNeighboringMines()



class Tile():
	def __init__(self):
		self.mine = False
		self.revealed = False
		self.marker = 0
		self.numNeighboringMines = 0


	def placeMine(self):
		self.mine = True


	def reveal(self):
		self.revealed = True


	def setNextMarker(self):
		self.marker = (self.marker + 1) % 3


	def increaseNeighboringMines(self):
		self.numNeighboringMines += 1


	def isMine(self):
		return self.mine


	def isRevealed(self):
		return self.revealed


	def getNumNeighboringMines(self):
		return self.numNeighboringMines


	def getMarker(self):
		return self.marker



class main():
	interface = GUI()
	interface.initGUI()
	interface.createMenu()
	interface.createGUI()
	interface.window.mainloop()