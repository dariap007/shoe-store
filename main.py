from app.db_init import init_if_needed
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow

init_if_needed()

if __name__ == "__main__":
    while True:
        user_info = None
        
        login_app = LoginWindow()
        login_app.mainloop()
        
        if hasattr(login_app, 'user_data') and login_app.user_data:
            user_info = login_app.user_data
        else:
            break

        if user_info:
            main_app = MainWindow(user_info)
            main_app.mainloop()

            if not hasattr(main_app, 'logged_out') or not main_app.logged_out:
                break
        else:
            break