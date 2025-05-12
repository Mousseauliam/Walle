import threading

class ModeManager:
    def __init__(self, robot, serveur):
        self.robot = robot
        self.serveur = serveur
        self.current_mode = None
        self.mode_thread = None
        self.lock = threading.Lock()

    def launch_mode(self, new_mode_module):
        with self.lock:
            self.stop_mode()
            self.current_mode = new_mode_module
            self.mode_thread = threading.Thread(target=self._run_mode)
            self.mode_thread.daemon = True
            self.mode_thread.start()
            print(f"[ModeManager] Launched mode: {new_mode_module.__name__}")

    def _run_mode(self):
        try:
            self.current_mode.run(self.robot,self.serveur)
        except Exception as e:
            print(f"[ModeManager] Mode crashed: {e}")

    def stop_mode(self):
        if self.current_mode:
            print(f"[ModeManager] Stopping mode: {self.current_mode.__name__}")
            try:
                self.current_mode.stop()
            except Exception as e:
                print(f"[ModeManager] Error stopping mode: {e}")
            if self.mode_thread and self.mode_thread.is_alive():
                self.mode_thread.join()
        self.current_mode = None
        self.mode_thread = None

    def get_active_mode_name(self):
        return self.current_mode.__name__ if self.current_mode else "None"
    
