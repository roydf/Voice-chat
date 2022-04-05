import ui
import vc_client
login_win = ui.Master("127.0.0.1")
login_win.open()
if login_win.did_connect:
    the_client = vc_client.Client("127.0.0.1", login_win.socket)
    main_program = ui.MainWindow(the_client, login_win.name)
    main_program.open()
    main_program.close()
