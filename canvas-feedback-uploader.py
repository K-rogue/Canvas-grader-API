from myGUI import CanvasGUI
from PyQt5.QtWidgets import QApplication

CANVAS_API_URL = "https://canvas.instructure.com/api/v1" #Enter API url here if not same 
CANVAS_ACCESS_TOKEN = "ACCESS-TOKEN"                     #Enter access token here

def main():
    app = QApplication([])
    ex = CanvasGUI(CANVAS_API_URL, CANVAS_ACCESS_TOKEN)

    app.exec_()

if __name__ == "__main__":
    main()
