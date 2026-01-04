from Views.main_view import MainView
from Controllers.controller import MainController


class App:
    
    def __init__(self):
        self.view = MainView()
        
        self.controller = MainController(self.view)
        
        self.view.set_presenter(self.controller)
    
    def run(self):
        self.view.run()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()