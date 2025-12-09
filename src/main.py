import sys
import random
import os
from PyQt5.QtWidgets import (QApplication, QLabel, QMenu, QAction, QDialog,
                             QVBoxLayout, QFormLayout, QSpinBox, QCheckBox,
                             QDialogButtonBox, QDoubleSpinBox, QHBoxLayout, QPushButton, QFrame, QWidget, QSizePolicy)
from PyQt5.QtGui import QMovie, QTransform, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QPointF, QUrl, QRect
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import platform
import shutil
import json

# KONFIGURASI PATH HELPER
if getattr(sys, 'frozen', False):
    # Jika dijalankan sebagai EXE (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Jika dijalankan sebagai Script Python biasa
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_asset_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)


def get_asset_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

# ==========================================
# CONFIGURATION MANAGER
# ==========================================
CONFIG_FILE = "config.json"

def get_config_path():
    # Simpan config di folder yang sama dengan exe/script
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, CONFIG_FILE)

def save_config(settings):
    try:
        with open(get_config_path(), 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Gagal menyimpan config: {e}")

def load_config():
    try:
        path = get_config_path()
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Gagal memuat config: {e}")
    return None

# CLASS AUTOSTART MANAGER (WINDOWS & LINUX)
class AutoStartManager:
    APP_NAME = "TrickcalChibiGoDesktop"

    @staticmethod
    def is_frozen():
        """Cek apakah aplikasi berjalan sebagai EXE/Binary (Compiled)"""
        return getattr(sys, 'frozen', False)

    @staticmethod
    def get_run_command():
        """Mendapatkan command yang tepat untuk dijalankan saat startup"""
        if AutoStartManager.is_frozen():
            # === MODE COMPILED (EXE) ===
            # Kita hanya perlu path ke file .exe itu sendiri
            # sys.executable di PyInstaller menunjuk ke file .exe
            return f'"{sys.executable}"'
        else:
            # === MODE SCRIPT (Python) ===
            # Command: "pythonw.exe" "main.py"
            python_exe = sys.executable
            # Di Windows, gunakan pythonw.exe agar tidak muncul console hitam saat startup
            if sys.platform == "win32" and "python.exe" in python_exe:
                python_exe = python_exe.replace("python.exe", "pythonw.exe")

            script_path = os.path.abspath(__file__)
            return f'"{python_exe}" "{script_path}"'

    @staticmethod
    def get_work_dir():
        """Mendapatkan folder kerja aplikasi"""
        if AutoStartManager.is_frozen():
            # Jika EXE, folder kerja adalah lokasi file .exe berada
            return os.path.dirname(sys.executable)
        else:
            # Jika Script, folder kerja adalah lokasi file .py berada
            return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def is_enabled():
        """Mengecek apakah autostart sudah aktif di Registry"""
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"Software\Microsoft\Windows\CurrentVersion\Run",
                                     0, winreg.KEY_READ)
                winreg.QueryValueEx(key, AutoStartManager.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                return False
            except Exception:
                return False
        elif sys.platform.startswith("linux"):
            autostart_path = os.path.expanduser(f"~/.config/autostart/{AutoStartManager.APP_NAME}.desktop")
            return os.path.exists(autostart_path)
        return False

    @staticmethod
    @staticmethod
    def toggle(enable):
        """Mengaktifkan atau Mematikan Autostart dengan Mode Silent"""
        # Ambil command dasar
        base_cmd = AutoStartManager.get_run_command()

        # [MODIFIKASI] Tambahkan flag --silent agar pas startup tidak muncul menu
        final_cmd = f'{base_cmd} --silent'

        work_dir = AutoStartManager.get_work_dir()

        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            if enable:
                winreg.SetValueEx(key, AutoStartManager.APP_NAME, 0, winreg.REG_SZ, final_cmd)
            else:
                try:
                    winreg.DeleteValue(key, AutoStartManager.APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)

        elif sys.platform.startswith("linux"):
            autostart_dir = os.path.expanduser("~/.config/autostart")
            file_path = os.path.join(autostart_dir, f"{AutoStartManager.APP_NAME}.desktop")

            if enable:
                if not os.path.exists(autostart_dir):
                    os.makedirs(autostart_dir)

                # Bersihkan quote untuk linux exec
                exec_cmd = final_cmd.replace('"', '')

                content = f"""[Desktop Entry]
    Type=Application
    Name=Trickcal Chibi GoDesktop
    Exec={exec_cmd}
    Path={work_dir}
    Terminal=false
    Hidden=false
    NoDisplay=false
    X-GNOME-Autostart-enabled=true
    Comment=Desktop Pet Application
    """
                with open(file_path, "w") as f:
                    f.write(content)
                os.chmod(file_path, 0o755)
            else:
                if os.path.exists(file_path):
                    os.remove(file_path)

# GLOBAL VARIABLES & SETTINGS
active_pets = []
global_pumpkin = None
is_muted = False
allow_struggle = True
global_scale = 1.0

# CLASS SETUP DIALOG
# ==========================================
# CLASS SETUP DIALOG (FINAL + ABOUT BUTTON)
# ==========================================
class SetupDialog(QDialog):
    def __init__(self, initial_settings=None):
        super().__init__()
        self.setWindowTitle("Trickcal Chibi GoDesktop Setup")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 460)  # Ukuran compact

        # STYLING
        self.setStyleSheet("""
            QDialog { background-color: #FFFDE7; }
            QLabel { color: #5D4037; font-weight: bold; font-family: 'Segoe UI', sans-serif; font-size: 13px; }

            QSpinBox, QDoubleSpinBox { 
                background-color: #424242; color: white; border-radius: 10px; 
                padding: 4px 8px; font-size: 13px; font-weight: bold; border: 2px solid #616161;
            }
            QSpinBox::up-button, QSpinBox::down-button, 
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0px; } 

            QCheckBox { color: #5D4037; font-size: 12px; font-weight: bold; spacing: 8px; }
            QCheckBox::indicator { width: 16px; height: 16px; background-color: #E0E0E0; border: 2px solid #BDBDBD; border-radius: 4px; }
            QCheckBox::indicator:checked { background-color: #03A9F4; border-color: #0288D1; }

            QPushButton#btnCancel { background-color: #FF80AB; color: white; border-radius: 12px; padding: 6px 15px; font-size: 14px; font-weight: bold; border: none; }
            QPushButton#btnCancel:hover { background-color: #F50057; }

            QPushButton#btnGo { background-color: #FFB74D; color: white; border-radius: 12px; padding: 6px 25px; font-size: 14px; font-weight: bold; border: none; }
            QPushButton#btnGo:hover { background-color: #FF9800; }

            /* Tombol About (?) */
            QPushButton#btnAbout {
                background-color: transparent;
                color: #5D4037;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #5D4037;
                border-radius: 12px;
                width: 24px;
                height: 24px;
            }
            QPushButton#btnAbout:hover {
                background-color: #5D4037;
                color: #FFFDE7;
            }

            QFrame#VLine { border: 1px dashed #BDBDBD; }
            QFrame#HLine { border: 1px solid #E0E0E0; }
        """)

        # Layout Utama
        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(20, 10, 20, 15)

        # 0. HEADER LAYOUT (Logo + Tombol ?)
        header_layout = QHBoxLayout()

        # Spacer kiri agar logo tetap di tengah (karena ada tombol di kanan)
        header_layout.addStretch()

        # LOGO
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_pix = QPixmap(get_asset_path("logo/main-logo.png"))
        if not logo_pix.isNull():
            logo_label.setPixmap(logo_pix.scaled(180, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("LOGO")
        header_layout.addWidget(logo_label)

        # Spacer kanan (sebelum tombol ?)
        header_layout.addStretch()

        # TOMBOL ABOUT (?)
        self.btn_about = QPushButton("?")
        self.btn_about.setObjectName("btnAbout")
        self.btn_about.setCursor(Qt.PointingHandCursor)
        self.btn_about.setFixedSize(24, 24)
        self.btn_about.clicked.connect(self.show_about_dialog)

        # Masukkan tombol ke layout vertikal kecil agar dia mojok kanan atas
        top_right_layout = QVBoxLayout()
        top_right_layout.addWidget(self.btn_about)
        top_right_layout.addStretch()  # Push ke atas

        header_layout.addLayout(top_right_layout)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(5)

        # 2. KARAKTER AREA
        char_container = QHBoxLayout()
        char_container.setSpacing(0)

        # --- KOLOM KIRI (SPEAKI) ---
        speaki_layout = QVBoxLayout()
        speaki_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        speaki_layout.setSpacing(5)

        lbl_speaki_img = QLabel()
        pix_speaki = QPixmap(get_asset_path("characters/speaki/Speaki-Cherrful.png"))
        lbl_speaki_img.setPixmap(pix_speaki.scaled(85, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        speaki_layout.addWidget(lbl_speaki_img, alignment=Qt.AlignCenter)

        row_speaki = QHBoxLayout()
        row_speaki.setAlignment(Qt.AlignCenter)
        row_speaki.addWidget(QLabel("Jumlah:"))
        self.spin_speaki = QSpinBox()
        self.spin_speaki.setRange(0, 5)
        self.spin_speaki.setValue(1)
        self.spin_speaki.setFixedWidth(50)
        self.spin_speaki.setAlignment(Qt.AlignCenter)
        row_speaki.addWidget(self.spin_speaki)
        speaki_layout.addLayout(row_speaki)

        # Checkbox Container Speaki
        check_container = QWidget()
        check_layout = QVBoxLayout(check_container)
        check_layout.setContentsMargins(0, 5, 0, 0)
        check_layout.setSpacing(4)

        self.check_pumpkin = QCheckBox("Pumpkin Ball")
        self.check_pumpkin.setChecked(True)
        self.check_pumpkin.stateChanged.connect(self.toggle_struggle_option)
        self.check_struggle = QCheckBox("Steal Skill")
        self.check_struggle.setChecked(True)

        check_layout.addWidget(self.check_pumpkin)
        check_layout.addWidget(self.check_struggle)
        check_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        speaki_layout.addWidget(check_container, alignment=Qt.AlignCenter)

        speaki_widget = QWidget()
        speaki_widget.setLayout(speaki_layout)
        char_container.addWidget(speaki_widget)

        # Garis Pemisah
        line = QFrame()
        line.setObjectName("VLine")
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        char_container.addWidget(line)

        # --- KOLOM KANAN (ERPIN) ---
        erpin_layout = QVBoxLayout()
        erpin_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        erpin_layout.setSpacing(5)

        lbl_erpin_img = QLabel()
        pix_erpin = QPixmap(get_asset_path("characters/erpin/Erpin-Cherrful.png"))
        lbl_erpin_img.setPixmap(pix_erpin.scaled(85, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        erpin_layout.addWidget(lbl_erpin_img, alignment=Qt.AlignCenter)

        row_erpin = QHBoxLayout()
        row_erpin.setAlignment(Qt.AlignCenter)
        row_erpin.addWidget(QLabel("Jumlah:"))
        self.spin_erpin = QSpinBox()
        self.spin_erpin.setRange(0, 5)
        self.spin_erpin.setValue(1)
        self.spin_erpin.setFixedWidth(50)
        self.spin_erpin.setAlignment(Qt.AlignCenter)
        row_erpin.addWidget(self.spin_erpin)
        erpin_layout.addLayout(row_erpin)
        erpin_layout.addStretch()

        erpin_widget = QWidget()
        erpin_widget.setLayout(erpin_layout)
        char_container.addWidget(erpin_widget)

        main_layout.addLayout(char_container)
        main_layout.addSpacing(5)

        # 3. GARIS PEMISAH GLOBAL
        h_line = QFrame()
        h_line.setObjectName("HLine")
        h_line.setFrameShape(QFrame.HLine)
        h_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(h_line)
        main_layout.addSpacing(5)

        # 4. GLOBAL SETTINGS
        global_layout = QVBoxLayout()
        global_layout.setSpacing(10)

        # Row 1: Scale
        row_scale = QHBoxLayout()
        row_scale.setAlignment(Qt.AlignCenter)
        row_scale.addWidget(QLabel("Size Scale:"))
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setRange(0.5, 1.2)
        self.spin_scale.setSingleStep(0.1)
        self.spin_scale.setValue(1.0)
        self.spin_scale.setFixedWidth(55)
        self.spin_scale.setAlignment(Qt.AlignCenter)
        row_scale.addWidget(self.spin_scale)
        global_layout.addLayout(row_scale)

        # Row 2: Checkboxes (Sound & Startup)
        row_checks = QHBoxLayout()
        row_checks.setAlignment(Qt.AlignCenter)
        row_checks.setSpacing(15)

        self.check_sound = QCheckBox("Enable Sound")
        self.check_sound.setChecked(True)
        row_checks.addWidget(self.check_sound)

        self.check_startup = QCheckBox("Run on Startup")
        # Default cek ke OS, bukan file config (untuk akurasi)
        self.check_startup.setChecked(AutoStartManager.is_enabled())
        row_checks.addWidget(self.check_startup)

        global_layout.addLayout(row_checks)
        main_layout.addLayout(global_layout)
        main_layout.addSpacing(10)

        # 5. TOMBOL AKSI
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setAlignment(Qt.AlignCenter)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_go = QPushButton("Go!")
        self.btn_go.setObjectName("btnGo")
        self.btn_go.setCursor(Qt.PointingHandCursor)
        self.btn_go.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_go)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # --- LOAD SAVED SETTINGS (JIKA ADA) ---
        if initial_settings:
            self.spin_speaki.setValue(initial_settings.get("count_speaki", 1))
            self.spin_erpin.setValue(initial_settings.get("count_erpin", 1))
            self.spin_scale.setValue(initial_settings.get("scale", 1.0))
            self.check_pumpkin.setChecked(initial_settings.get("pumpkin", True))
            self.check_struggle.setChecked(initial_settings.get("struggle", True))
            self.check_sound.setChecked(initial_settings.get("sound", True))

    def show_about_dialog(self):
        about = QDialog(self)
        about.setWindowTitle("About Developer")
        about.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        about.setFixedSize(300, 150)
        about.setStyleSheet("""
            QDialog { background-color: #FFFDE7; }
            QLabel { color: #5D4037; font-size: 14px; }
            QPushButton { 
                background-color: #FFB74D; color: white; 
                border-radius: 8px; padding: 5px 15px; font-weight: bold; border: none;
            }
            QPushButton:hover { background-color: #FF9800; }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        lbl_info = QLabel("<b>Trickcal Chibi GoDesktop</b><br><br>"
                          "Created by: <b>Jeremi Herodian</b><br>"
                          "Github: <a href='https://www.github.com/JrHero14' style='color:#03A9F4;'>www.github.com/JrHero14</a>")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setOpenExternalLinks(True)  # Agar link bisa diklik

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(about.accept)

        layout.addWidget(lbl_info)
        layout.addSpacing(15)
        layout.addWidget(btn_close)

        about.setLayout(layout)
        about.exec_()

    def toggle_struggle_option(self):
        has_pumpkin = self.check_pumpkin.isChecked()
        self.check_struggle.setEnabled(has_pumpkin)
        if not has_pumpkin: self.check_struggle.setChecked(False)

    def get_settings(self):
        return {
            "count_speaki": self.spin_speaki.value(),
            "count_erpin": self.spin_erpin.value(),
            "scale": self.spin_scale.value(),
            "pumpkin": self.check_pumpkin.isChecked(),
            "struggle": self.check_struggle.isChecked(),
            "sound": self.check_sound.isChecked(),
            "startup": self.check_startup.isChecked()
        }

# FUNGSI SPAWN
def spawn_pet(pet_class_name="Speaki"):
    screen = QApplication.primaryScreen().availableGeometry()
    new_id = len(active_pets) + 1

    # Pilih class berdasarkan nama
    if pet_class_name == "Erpin":
        new_pet = Erpin(toy=global_pumpkin, pet_id=new_id)
    else:
        new_pet = Speaki(toy=global_pumpkin, pet_id=new_id)

    margin = int(100 * global_scale)
    spawn_x = random.randint(margin, screen.width() - margin)
    spawn_y = screen.height() - 200
    new_pet.move(spawn_x, spawn_y)
    new_pet.show()
    active_pets.append(new_pet)


# CLASS PUMKIN
class DesktopToy(QLabel):
    def __init__(self, icon_relative_path, size=100):
        super().__init__()

        # Setup Window Flags (Linux/Windows)
        if sys.platform.startswith('linux'):
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        self.setAttribute(Qt.WA_TranslucentBackground)

        # Simpan path icon normal & soup
        self.icon_normal = icon_relative_path
        # Asumsi gambar soup ada di folder yang sama dengan pumpkin
        self.icon_soup = "characters/speaki/pumkin-soup.png"
        self.is_soup = False  # Status apakah sedang jadi soup

        self.size_val = size
        full_path = get_asset_path(self.icon_normal)
        self.pixmap = QPixmap(full_path)

        final_size = int(size * global_scale)
        self.target_size = QSize(final_size, final_size)
        self.setPixmap(self.pixmap.scaled(self.target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.resize(self.target_size)

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.gravity = 1.0 * global_scale
        self.floor_y = 0
        self.bounce = 0.7
        self.friction = 0.98
        self.is_dragging = False
        self.is_held = False
        self.holder = None
        self.drag_start = QPointF(0, 0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.physics_loop)
        self.timer.start(16)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            if self.holder: self.holder.release_toy_forced()
            self.is_held = False
            self.holder = None
            self.drag_start = event.globalPos() - self.frameGeometry().topLeft()
            self.vx = 0
            self.vy = 0
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #2b2b2b; color: white; border: 1px solid #555; padding: 5px; } QMenu::item:selected { background-color: #444; }")

        # Opsi ganti ke Soup
        action_text = "Change to Pumpkin" if self.is_soup else "Change to Soup"
        menu.addAction(action_text, self.toggle_soup)

        menu.addSeparator()
        menu.addAction("Exit Program", QApplication.quit)
        menu.exec_(pos)

    def toggle_soup(self):
        self.is_soup = not self.is_soup
        target_icon = self.icon_soup if self.is_soup else self.icon_normal

        # Update Gambar
        full_path = get_asset_path(target_icon)
        self.pixmap = QPixmap(full_path)

        # Resize ulang sesuai scale saat ini
        final_size = int(self.size_val * global_scale)
        self.target_size = QSize(final_size, final_size)
        self.setPixmap(self.pixmap.scaled(self.target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Jika sedang dipegang speaki saat berubah jadi soup, paksa lepas!
        if self.is_soup and self.holder:
            self.holder.throw_toy(force=5.0)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_pos = event.globalPos() - self.drag_start
            self.vx = (new_pos.x() - self.x()) * 0.5
            self.vy = (new_pos.y() - self.y()) * 0.5
            self.move(new_pos)
            self.pos_x = float(new_pos.x())
            self.pos_y = float(new_pos.y())
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False;
        event.accept()

    def physics_loop(self):
        self.raise_()
        if self.pos_x == 0: self.pos_x = float(self.x())
        if self.pos_y == 0: self.pos_y = float(self.y())

        if self.is_held: return
        if not self.is_dragging:
            screen = QApplication.primaryScreen().availableGeometry()
            self.floor_y = screen.height() + screen.y() - self.height()
            self.vy += self.gravity
            self.pos_y += self.vy
            self.pos_x += self.vx

            if self.pos_y >= self.floor_y - 5:
                self.vx *= self.friction
            else:
                self.vx *= 0.995

            if self.pos_y >= self.floor_y:
                self.pos_y = self.floor_y
                if self.vy > 2:
                    self.vy = -self.vy * self.bounce
                else:
                    self.vy = 0

            if self.pos_x <= screen.x():
                self.pos_x = screen.x()
                self.vx = -self.vx * self.bounce
            elif self.pos_x + self.width() >= screen.width() + screen.x():
                self.pos_x = screen.width() + screen.x() - self.width()
                self.vx = -self.vx * self.bounce
            self.move(int(self.pos_x), int(self.pos_y))


# ==========================================
# BASE CLASS (PARENT)
# ==========================================
class BasePet(QLabel):
    def __init__(self, toy=None, pet_id=1, character_folder="default"):
        super().__init__()
        self.toy = toy
        self.pet_id = pet_id
        self.character_folder = character_folder
        self.scale = global_scale

        if sys.platform.startswith('linux'):
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.vx = 0.0
        self.vy = 0.0

        self.gravity = 1.5 * self.scale
        self.floor_y = 0
        self.on_ground = False
        self.is_dragging = False
        self.anchor_offset = QPointF(0, 0)
        self.facing_right = True if pet_id % 2 != 0 else False

        self.player = QMediaPlayer()
        self.player.setVolume(70)
        self.player.stateChanged.connect(self.on_media_state_changed)

        base_size = 150
        scaled_size = int(base_size * self.scale)
        self.movie_size = QSize(scaled_size, scaled_size)

        self.current_movie = None
        self.resize(self.movie_size)
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(16)

    def update_orientation(self):
        pass

    def load_movie(self, filename):
        path = get_asset_path(f"characters/{self.character_folder}/{filename}")
        movie = QMovie(path)
        if not movie.isValid(): print(f"Warning: Animasi {filename} tidak valid")
        movie.setScaledSize(self.movie_size)
        movie.frameChanged.connect(self.update_frame)
        return movie

    def play_sound(self, filename):
        if is_muted: return
        if hasattr(self,
                   'state') and self.state == "STRUGGLE" and self.player.state() == QMediaPlayer.PlayingState: return
        if self.player.state() == QMediaPlayer.PlayingState: self.player.stop()

        full_path = get_asset_path(f"characters/{self.character_folder}/sound/{filename}")
        if not os.path.exists(full_path): return
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(full_path)))
        self.player.play()

    def update_frame(self):
        if self.current_movie:
            pixmap = self.current_movie.currentPixmap()
            if self.facing_right: pixmap = pixmap.transformed(QTransform().scale(-1, 1))
            self.setPixmap(pixmap)

    def change_animation(self, new_movie):
        if self.current_movie == new_movie: return
        if self.current_movie: self.current_movie.stop()
        self.current_movie = new_movie
        self.current_movie.start()
        self.update_frame()

    def on_media_state_changed(self, new_state):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_left_click(event)
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        if self.is_dragging: event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False;
        event.accept()

    def on_left_click(self, event):
        self.is_dragging = True
        self.on_ground = False
        self.anchor_offset = QPointF(event.pos())
        event.accept()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #2b2b2b; color: white; border: 1px solid #555; }")
        menu.addAction("Exit Program", QApplication.quit)
        menu.exec_(pos)

    def apply_dragging_physics(self):
        m = self.cursor().pos()
        t = m - self.anchor_offset
        dx = t.x() - self.pos_x
        dy = t.y() - self.pos_y
        self.vx += dx * 0.15
        self.vy += dy * 0.15
        self.vx *= 0.80
        self.vy *= 0.80
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.move(int(self.pos_x), int(self.pos_y))

    def apply_falling_physics(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.floor_y = screen.height() + screen.y() - self.height()
        self.vy += self.gravity
        self.pos_y += self.vy
        self.pos_x += self.vx
        if self.pos_y >= self.floor_y:
            self.pos_y = self.floor_y
            self.handle_landing()
        else:
            self.on_ground = False
        if self.pos_x <= screen.x():
            self.pos_x = screen.x()
            self.vx = -self.vx * 0.5
            self.on_wall_hit('left')
        elif self.pos_x + self.width() >= screen.width() + screen.x():
            self.pos_x = screen.width() + screen.x() - self.width()
            self.vx = -self.vx * 0.5
            self.on_wall_hit('right')

    def handle_landing(self):
        self.vy = 0;
        self.vx *= 0.90;
        self.on_ground = True

    def on_wall_hit(self, side):
        pass

    def game_loop(self):
        if self.pos_x == 0: self.pos_x = float(self.x())
        if self.pos_y == 0: self.pos_y = float(self.y())
        self.update_orientation()
        if self.is_dragging:
            self.apply_dragging_physics()
        else:
            self.apply_falling_physics()
            self.behavior_tick()
        self.move(int(self.pos_x), int(self.pos_y))

    def behavior_tick(self):
        pass


# ==========================================
# CHARACTER: SPEAKI
# ==========================================
class Speaki(BasePet):
    def __init__(self, toy=None, pet_id=1):
        super().__init__(toy, pet_id, character_folder="speaki")
        self.movie_cheerful = self.load_movie("Speaki-Cherrful.png")
        self.movie_cry = self.load_movie("Speaki-Cry.png")
        self.movie_happy = self.load_movie("Speaki-Happu.png")

        self.footstep_sounds = ["walk-1.mp3", "walk-2.mp3", "walk-3.mp3"]
        self.jump_sound = "jump.mp3"
        self.drag_sound = "cry-drag.mp3"
        self.angry_sounds = ["angry-full.mp3", "angry-half.mp3"]

        self.tantrum_sound_special = "Speaki-Euu.mp3"

        self.current_movie = self.movie_cheerful
        self.current_movie.start()
        self.update_frame()
        self.state = "IDLE"
        self.state_timer = 100

        self.walk_speed = 3.0 * self.scale
        self.run_speed = 7.0 * self.scale

        self.was_falling = False
        self.is_holding_toy = False
        self.hold_timer = 0
        self.rival_pet = None
        self.struggle_cooldown = 0

        # Timer untuk mode nekat (lompat melewati soup)
        self.soup_panic_timer = 0

    def update_orientation(self):
        # Saat menghindari soup, orientasi diatur otomatis oleh pergerakan
        if self.state == "AVOIDING_SOUP":
            if abs(self.vx) > 0.5:
                if self.vx > 0.5 and not self.facing_right:
                    self.facing_right = True;
                    self.update_frame()
                elif self.vx < -0.5 and self.facing_right:
                    self.facing_right = False;
                    self.update_frame()
            return

        if abs(self.vx) > 0.5 and self.state != "STRUGGLE" and self.state != "RUNNING_AWAY":
            if self.vx > 0.5 and not self.facing_right:
                self.facing_right = True;
                self.update_frame()
            elif self.vx < -0.5 and self.facing_right:
                self.facing_right = False;
                self.update_frame()

    def end_tantrum(self):
        if self.state == "ANGRY":
            self.state = "IDLE"
            self.change_animation(self.movie_cheerful)
            self.state_timer = random.randint(60, 100)

    def on_left_click(self, event):
        if self.state == "ANGRY" or self.state == "STRUGGLE": return
        if self.is_holding_toy: self.throw_toy(force=2.0)
        super().on_left_click(event)
        self.was_falling = True
        self.state = "IDLE"
        self.change_animation(self.movie_cry)
        self.play_sound(self.drag_sound)

    def on_media_state_changed(self, new_state):
        if new_state == QMediaPlayer.StoppedState and self.state == "ANGRY": self.end_tantrum()

    def on_wall_hit(self, side):
        # Jika nabrak tembok saat sedang panic jump, matikan panic agar tidak stuck
        if self.state == "AVOIDING_SOUP" and self.soup_panic_timer > 0:
            self.soup_panic_timer = 0

        if side == 'left':
            self.state = "WALK_RIGHT"
        elif side == 'right':
            self.state = "WALK_LEFT"

    def handle_landing(self):
        if self.state == "JUMPING":
            self.vy = 0
            self.vx *= 0.5
            self.on_ground = True
            self.state = "IDLE"
            self.change_animation(self.movie_cheerful)
        elif self.state == "ANGRY":
            self.on_ground = True;
            self.vx = 0
        elif self.state == "AVOIDING_SOUP":
            self.on_ground = True
            self.vy = 0
            # Jangan reset state di sini, biarkan handle_avoid_soup yang menentukan
            # apakah sudah aman atau belum
        else:
            if self.vy > 2:
                self.vy = -self.vy * 0.5
                self.vx *= 0.8
                self.on_ground = False
                self.change_animation(self.movie_cry)
            else:
                self.vy = 0
                self.vx *= 0.90
                self.on_ground = True
                if self.was_falling: self.was_falling = False; self.start_angry_tantrum(); return
                if abs(self.vx) < 1 and self.state != "ANGRY" and self.state != "RUNNING_AWAY":
                    self.change_animation(self.movie_cheerful)

    def behavior_tick(self):
        if self.struggle_cooldown > 0: self.struggle_cooldown -= 1

        # [LOGIC] Menghindar Soup (Prioritas Tertinggi)
        if self.toy and getattr(self.toy, 'is_soup', False) and self.state != "ANGRY" and self.state != "STRUGGLE":
            self.handle_avoid_soup()
            if self.state == "AVOIDING_SOUP": return

        if self.state == "STRUGGLE":
            if self.rival_pet not in active_pets: self.resolve_struggle(); return
            self.handle_struggle_behavior()
            return
        if self.state == "RUNNING_AWAY": self.handle_running_away()

        if self.on_ground and self.state not in ["JUMPING", "ANGRY", "RUNNING_AWAY", "AVOIDING_SOUP"]:
            if self.state == "CHASING_TOY":
                self.handle_chasing_behavior()
            else:
                self.update_idle_walk_behavior()
        elif self.state == "ANGRY":
            if self.on_ground: self.vy = -random.uniform(5, 10) * self.scale; self.on_ground = False

        if not self.is_holding_toy: self.check_toy_collision()

        if self.is_holding_toy and self.toy and self.state != "STRUGGLE":
            if getattr(self.toy, 'is_soup', False):
                self.throw_toy(force=8.0)
                self.trigger_escape_jump()
                return

            if self.on_ground and random.random() < 0.0005: self.trigger_escape_jump()

            carry_offset_x = 40 * self.scale if self.facing_right else -40 * self.scale
            carry_offset_y = 60 * self.scale

            self.toy.pos_x = self.pos_x + (self.width() / 2) + carry_offset_x - (self.toy.width() / 2)
            self.toy.pos_y = self.pos_y + carry_offset_y
            self.toy.move(int(self.toy.pos_x), int(self.toy.pos_y))
            self.hold_timer -= 1
            if self.hold_timer <= 0: self.throw_toy(force=12.0)

    # [FIX INVISIBLE WALL & PANIC JUMP]
    def handle_avoid_soup(self):
        # 1. Jika sedang Panic Mode, biarkan timer jalan dan momentum fisika bekerja
        if self.soup_panic_timer > 0:
            self.soup_panic_timer -= 1
            self.state = "AVOIDING_SOUP"

            # [TAMBAHAN] Pastikan tetap lari kencang saat panic (agar tidak berhenti di udara)
            if self.vx != 0:
                direction = 1 if self.vx > 0 else -1
                self.vx = (self.run_speed * 1.5) * direction
            return

            # 2. Jika sedang di udara, biarkan fisika bekerja (jangan ganggu VX)
        if not self.on_ground:
            return

        center_self = self.pos_x + self.width() / 2
        center_toy = self.toy.pos_x + self.toy.width() / 2
        dist = center_self - center_toy

        safe_dist = 300 * self.scale

        # Jika dalam bahaya (terlalu dekat dengan soup)
        if abs(dist) < safe_dist:
            self.state = "AVOIDING_SOUP"
            self.change_animation(self.movie_cry)

            # Tentukan arah lari normal (menjauhi soup)
            flee_dir = 1 if dist > 0 else -1

            # Cek Tembok (Apakah terpojok?)
            screen = QApplication.primaryScreen().availableGeometry()
            margin = 60 * self.scale

            is_cornered_left = (self.pos_x < screen.x() + margin and flee_dir == -1)
            is_cornered_right = (self.pos_x + self.width() > screen.width() + screen.x() - margin and flee_dir == 1)

            if is_cornered_left or is_cornered_right:
                # === MODE NEKAT (PANIC JUMP) ===
                # Terpojok! Balik arah (mendekati soup) untuk melewatinya
                flee_dir = -flee_dir

                # Lompat HANYA 1 KALI saat masih di tanah
                if self.on_ground:
                    self.vy = -14.0 * self.scale
                    self.vx = (self.run_speed * 1.8) * flee_dir
                    self.play_sound(self.jump_sound)
                    self.on_ground = False

                # Set timer agar selama 1.5 detik (90 frame) dia lari buta tanpa mengecek jarak
                self.soup_panic_timer = 90
                return

            # Normal Avoidance: HANYA LARI (Lompatan kecil dihapus)
            self.vx = self.run_speed * flee_dir

        elif self.state == "AVOIDING_SOUP":
            # Jika jarak sudah aman, kembali normal
            self.state = "IDLE"
            self.vx = 0
            self.soup_panic_timer = 0
            self.change_animation(self.movie_cheerful)

    def start_angry_tantrum(self):
        self.state = "ANGRY"
        self.vx = 0
        self.change_animation(self.movie_cry)
        self.state_timer = 120
        if self.is_holding_toy: self.throw_toy(force=5.0)

        if is_muted:
            QTimer.singleShot(2000, self.end_tantrum)
        else:
            if random.random() < 0.8:
                self.play_sound(self.tantrum_sound_special)
            else:
                self.play_sound(random.choice(self.angry_sounds))

    def trigger_jump(self):
        if self.on_ground:
            self.state = "JUMPING"
            self.on_ground = False
            self.vy = -15.0 * self.scale
            self.change_animation(self.movie_happy)
            self.play_sound(self.jump_sound)

    def trigger_escape_jump(self):
        sw = QApplication.primaryScreen().availableGeometry().width()
        jd = 1 if self.pos_x < 200 else (-1 if self.pos_x > sw - 200 else (1 if random.random() > 0.5 else -1))
        self.vy = -15.0 * self.scale
        self.vx = 15.0 * self.scale * jd
        self.on_ground = False
        self.state = "JUMPING"
        self.facing_right = True if jd == 1 else False
        self.change_animation(self.movie_happy)
        self.play_sound(self.jump_sound)
        self.update_frame()

    def update_idle_walk_behavior(self):
        self.state_timer -= 1
        should_chase = False

        if self.toy and not self.is_holding_toy and not getattr(self.toy, 'is_soup', False):
            if allow_struggle:
                should_chase = True
            elif not self.toy.is_held:
                should_chase = True

        if should_chase and random.random() < 0.005: self.start_chasing_toy(); return

        jump_chance = 0.005 if global_pumpkin else 0.0005
        if not self.is_holding_toy and self.state in ["WALK_LEFT", "WALK_RIGHT"]:
            if random.random() < jump_chance: self.trigger_jump(); return

        if self.state_timer <= 0:
            ar = random.randint(1, 100)
            if ar <= 5:
                self.state = "IDLE";
                self.state_timer = random.randint(60, 180)
            elif ar <= 52:
                self.state = "WALK_LEFT";
                self.state_timer = random.randint(300, 800)
            else:
                self.state = "WALK_RIGHT";
                self.state_timer = random.randint(300, 800)
            if self.state != "IDLE":
                self.play_sound(random.choice(self.footstep_sounds))
            else:
                self.player.stop()

        if self.state == "IDLE":
            self.vx *= 0.8
        elif self.state == "WALK_LEFT":
            self.vx = (self.vx * 0.9) + (-self.walk_speed * 0.1)
        elif self.state == "WALK_RIGHT":
            self.vx = (self.vx * 0.9) + (self.walk_speed * 0.1)

    def start_chasing_toy(self):
        if not self.toy or self.is_holding_toy or getattr(self.toy, 'is_soup', False): return
        self.state = "CHASING_TOY"
        self.state_timer = 250

    def handle_chasing_behavior(self):
        if not self.toy or getattr(self.toy, 'is_soup', False): self.state = "IDLE"; return

        if not allow_struggle and self.toy.is_held:
            self.state = "IDLE"
            if self.current_movie != self.movie_cheerful: self.change_animation(self.movie_cheerful)
            return
        self.state_timer -= 1
        if self.state_timer <= 0: self.state = "IDLE"; return
        diff = (self.toy.pos_x + self.toy.width() / 2) - (self.pos_x + self.width() / 2)
        if diff > 10:
            self.vx = self.run_speed
        elif diff < -10:
            self.vx = -self.run_speed
        else:
            self.vx *= 0.5

    def handle_running_away(self):
        self.state_timer -= 1
        self.vx = self.run_speed * 1.5 * (1 if self.facing_right else -1)
        if self.state_timer <= 0: self.state = "IDLE"
        self.change_animation(self.movie_cheerful)

    def catch_toy(self):
        if not self.toy: return
        self.is_holding_toy = True
        self.toy.is_held = True
        self.toy.holder = self
        self.toy.vx = 0
        self.toy.vy = 0
        self.hold_timer = random.randint(200, 450)
        if self.state != "RUNNING_AWAY":
            self.state = "WALK_RIGHT" if self.facing_right else "WALK_LEFT"
            self.change_animation(self.movie_cheerful)

    def throw_toy(self, force=12.0):
        if not self.toy: return
        self.is_holding_toy = False
        self.toy.is_held = False
        self.toy.holder = None
        final_force = force * self.scale
        self.toy.vx = final_force * (1 if self.facing_right else -1)
        self.toy.vy = -10.0 * self.scale
        self.state = "IDLE"
        self.vx = 0
        self.play_sound(self.jump_sound)

    def release_toy_forced(self):
        self.is_holding_toy = False;
        self.state = "IDLE"

    def check_toy_collision(self):
        if not self.toy or self.struggle_cooldown > 0 or self.state in ["ANGRY", "RUNNING_AWAY",
                                                                        "AVOIDING_SOUP"]: return
        if getattr(self.toy, 'is_soup', False): return

        if self.geometry().intersects(self.toy.geometry()):
            if not self.toy.is_held:
                if self.state == "CHASING_TOY":
                    if random.random() < 0.2:
                        self.catch_toy()
                    else:
                        self.kick_toy()
                else:
                    if random.random() < 0.02:
                        self.kick_toy(weak=True)
                    else:
                        if self.vx != 0: self.toy.vx = self.vx * 1.2
            elif self.toy.holder and self.toy.holder != self:
                opponent = self.toy.holder
                if self.state != "STRUGGLE" and opponent.state != "STRUGGLE" and opponent.state != "ANGRY":
                    if allow_struggle and random.random() < 0.05:
                        self.start_struggle(opponent)
                        opponent.start_struggle(self)

    def kick_toy(self, weak=False):
        dx = self.toy.geometry().center().x() - self.geometry().center().x()
        self.facing_right = True if dx > 0 else False
        self.update_frame()
        if not weak: self.state = "IDLE"; self.change_animation(self.movie_happy); self.state_timer = 60

        force = (5.0 if weak else 18.0) * self.scale
        kick_y = (-5.0 if weak else -15.0) * self.scale

        self.toy.vx = (force + abs(self.vx)) * (1 if dx > 0 else -1)
        self.toy.vy = kick_y
        self.vx = 0

    def start_struggle(self, other_pet):
        self.state = "STRUGGLE"
        self.rival_pet = other_pet
        self.state_timer = 10
        self.vx = 0
        self.vy = 0
        if self.is_holding_toy:
            self.change_animation(self.movie_cry)
        else:
            self.change_animation(self.movie_happy)

    def handle_struggle_behavior(self):
        self.state_timer -= 1
        if self.is_holding_toy and self.current_movie != self.movie_cry:
            self.change_animation(self.movie_cry)
        elif not self.is_holding_toy and self.current_movie != self.movie_happy:
            self.change_animation(self.movie_happy)

        if self.is_holding_toy and self.toy:
            off_x = 40 * self.scale if self.facing_right else -40 * self.scale
            off_y = 60 * self.scale
            self.toy.move(int(self.pos_x + (self.width() / 2) + off_x - (self.toy.width() / 2) + random.randint(-5, 5)),
                          int(self.pos_y + off_y + random.randint(-5, 5)))

        if not self.is_holding_toy and self.rival_pet:
            dist = 80 * self.scale
            tx = self.rival_pet.pos_x + (dist if self.rival_pet.facing_right else -dist)
            self.pos_x = self.pos_x * 0.85 + tx * 0.15
            target_face = not self.rival_pet.facing_right
            if self.facing_right != target_face: self.facing_right = target_face; self.update_frame()

        self.move(int(self.pos_x + random.randint(-4, 4)), int(self.pos_y + random.randint(-1, 1)))
        if self.state_timer <= 0: self.resolve_struggle()

    def resolve_struggle(self):
        if not self.is_holding_toy and self.rival_pet and self.rival_pet.is_holding_toy:
            self.rival_pet.release_toy_forced()
            self.catch_toy()
            self.struggle_cooldown = 300
            if self.rival_pet: self.rival_pet.struggle_cooldown = 300; self.rival_pet.start_angry_tantrum()
            self.state = "RUNNING_AWAY"
            self.facing_right = False if self.rival_pet and self.rival_pet.pos_x > self.pos_x else True
            self.update_frame()
            self.state_timer = 300
            self.play_sound(self.jump_sound)
            self.change_animation(self.movie_cheerful)
        elif self.state == "STRUGGLE":
            self.state = "IDLE";
            self.change_animation(self.movie_cheerful)
        self.rival_pet = None


# ==========================================
# CHARACTER: ERPIN
# ==========================================
class Erpin(BasePet):
    def __init__(self, toy=None, pet_id=1):
        super().__init__(toy, pet_id, character_folder="erpin")
        # Load Assets for Erpin
        self.movie_cheerful = self.load_movie("Erpin-Cherrful.png")  # Walk/Idle
        self.movie_cry = self.load_movie("Erpin-Cry.png")  # Tantrum/Punched
        self.movie_happy = self.load_movie("Erpin-Happy.png")  # Jump/Chat
        self.movie_sleep = self.load_movie("Erpin-Sleeping.png")

        # Sound settings
        self.punch_sounds = [
            ("Erpin-Punch-1.mp3", 250),
            ("Erpin-Punch-2.mp3", 312)
        ]

        self.walk_sound = "Erpin-humu.mp3"

        self.current_movie = self.movie_cheerful
        self.current_movie.start()

        self.state = "IDLE"
        self.state_timer = 100
        self.walk_speed = 2.5 * self.scale

        # Variabel interaksi
        self.shake_frames = 0
        self.chat_partner = None
        self.chat_cooldown = 0  # Jeda waktu agar tidak keseringan ngobrol

    def update_orientation(self):
        # Saat interaksi (approach/chat), orientasi diatur manual
        if self.state in ["CHATTING", "APPROACHING"]:
            return

        if self.is_dragging or abs(self.vx) > 0.5:
            if self.vx > 0.5 and not self.facing_right:
                self.facing_right = True
                self.update_frame()
            elif self.vx < -0.5 and self.facing_right:
                self.facing_right = False
                self.update_frame()

    def on_wall_hit(self, side):
        # Jangan ubah state jika sedang sibuk interaksi
        if self.state in ["TANTRUM", "CHATTING", "APPROACHING"]:
            return

        if side == 'left':
            self.state = "WALK_RIGHT"
        elif side == 'right':
            self.state = "WALK_LEFT"

    def on_left_click(self, event):
        # Putuskan interaksi jika di-klik
        if self.state in ["CHATTING", "APPROACHING"]:
            self.end_chat()
            if self.chat_partner:
                self.chat_partner.end_chat()

        self.start_tantrum()
        self.shake_frames = 15
        super().on_left_click(event)

    def start_sleeping(self):
        """Memulai event tidur langka (30s - 60s)"""
        self.state = "SLEEPING"
        self.vx = 0  # Berhenti bergerak

        # Random durasi antara 30 detik s/d 60 detik (asumsi 60 FPS)
        self.state_timer = random.randint(1800, 3600)

        self.change_animation(self.movie_sleep)

    def start_tantrum(self):
        self.state = "TANTRUM"
        self.change_animation(self.movie_cry)

        sound_file, duration = random.choice(self.punch_sounds)
        self.state_timer = duration
        self.play_sound(sound_file)
        self.vx = 0

    def initiate_approach(self, partner):
        """Mulai fase mendekat"""
        self.state = "APPROACHING"
        self.chat_partner = partner
        self.state_timer = 300  # Timeout jika gagal mendekat
        self.change_animation(self.movie_cheerful)

    def start_chat_sequence(self):
        """Mulai fase ngobrol (setelah dekat)"""
        self.state = "CHATTING"
        self.vx = 0
        self.state_timer = 312  # Durasi ngobrol ~5 detik
        self.change_animation(self.movie_happy)

    def end_chat(self):
        """Selesai interaksi"""
        self.state = "IDLE"
        self.chat_partner = None
        self.change_animation(self.movie_cheerful)
        self.state_timer = 100
        self.chat_cooldown = 500  # Cooldown ~8 detik sebelum bisa ngobrol lagi

    def trigger_jump(self):
        if self.on_ground:
            self.state = "JUMPING"
            self.on_ground = False
            self.vy = -15.0 * self.scale
            self.change_animation(self.movie_happy)

    def handle_landing(self):
        if self.state == "SLEEPING":
            self.vx = 0
            self.vy = 0
            self.on_ground = True
            return

        if self.state == "JUMPING":
            self.vy = 0
            self.vx *= 0.5
            self.on_ground = True
            self.state = "IDLE"
            self.change_animation(self.movie_cheerful)
        elif self.state in ["CHATTING", "APPROACHING"]:
            self.on_ground = True
            if self.state == "CHATTING": self.vx = 0
        else:
            if self.vy > 2:
                self.vy = -self.vy * 0.5
                self.vx *= 0.8
                self.on_ground = False
                if self.state != "TANTRUM":
                    self.change_animation(self.movie_cry)
            else:
                self.vy = 0
                self.vx *= 0.90
                self.on_ground = True
                if self.state == "TANTRUM":
                    self.vx = 0
                else:
                    if abs(self.vx) < 1:
                        self.change_animation(self.movie_cheerful)

    def game_loop(self):
        super().game_loop()
        if self.shake_frames > 0:
            shake_range = int(5 * self.scale)
            shake_x = random.randint(-shake_range, shake_range)
            shake_y = random.randint(-shake_range, shake_range)
            self.move(self.x() + shake_x, self.y() + shake_y)
            self.shake_frames -= 1

    def behavior_tick(self):
        self.state_timer -= 1
        if self.chat_cooldown > 0: self.chat_cooldown -= 1

        if self.state == "TANTRUM":
            if self.on_ground:
                self.vy = -random.uniform(5, 10) * self.scale
                self.on_ground = False
            if self.state_timer <= 0:
                self.state = "IDLE"
                self.change_animation(self.movie_cheerful)
            return

        if self.state == "SLEEPING":
            self.vx = 0  # Pastikan diam
            if self.state_timer <= 0:
                # Waktunya bangun
                self.state = "IDLE"
                self.change_animation(self.movie_cheerful)
                self.state_timer = 100
            return

        if self.state == "APPROACHING":
            if not self.chat_partner or self.chat_partner not in active_pets or self.chat_partner.state not in [
                "APPROACHING", "CHATTING"]:
                self.end_chat()
                return

            dist = self.chat_partner.pos_x - self.pos_x
            target_dist = 90 * self.scale

            if abs(dist) > target_dist:
                direction = 1 if dist > 0 else -1
                self.vx = self.walk_speed * direction

                self.facing_right = (direction == 1)
                self.update_frame()
            else:
                self.start_chat_sequence()

            if self.state_timer <= 0:
                self.end_chat()

            return

        if self.state == "CHATTING":
            if self.state_timer <= 0 or (self.chat_partner and self.chat_partner not in active_pets):
                self.end_chat()
                return

            # Pastikan selalu saling berhadapan
            if self.chat_partner:
                target_face = self.pos_x < self.chat_partner.pos_x
                if self.facing_right != target_face:
                    self.facing_right = target_face
                    self.update_frame()

            # Lompat kecil senang
            if self.on_ground and random.random() < 0.08:
                self.vy = -10.0 * self.scale
                self.on_ground = False

            return

            # 4. Normal Idle/Walk
        if self.on_ground and self.state != "JUMPING":
            self.check_for_friends()  # Cek teman sekitar
            self.update_idle_walk_behavior()

    def check_for_friends(self):
        # Jika sedang cooldown, jangan cari teman dulu
        if self.chat_cooldown > 0: return

        for pet in active_pets:
            if pet is not self and isinstance(pet, Erpin):
                # Hanya ajak teman yang sedang nganggur
                if pet.state in ["IDLE", "WALK_LEFT", "WALK_RIGHT"] and pet.chat_cooldown <= 0:

                    dist = abs(self.pos_x - pet.pos_x)

                    if dist < 300 * self.scale:
                        # Peluang trigger event (kecil per frame, tapi pasti kena eventually)
                        if random.random() < 0.005:
                            self.initiate_approach(pet)
                            pet.initiate_approach(self)
                            break

    def update_idle_walk_behavior(self):
        if random.random() < 0.005:
            self.trigger_jump()
            return

        if self.state_timer <= 0:
            ar = random.randint(1, 100)

            if ar <= 5:
                self.start_sleeping()
            elif ar <= 15:
                self.state = "IDLE"
                self.state_timer = random.randint(60, 180)
            elif ar <= 58:  # (sekitar 43% jalan kiri)
                self.state = "WALK_LEFT"
                self.state_timer = random.randint(100, 400)
                if random.random() < 0.5: self.play_sound(self.walk_sound)
            else:  # (sisanya jalan kanan)
                self.state = "WALK_RIGHT"
                self.state_timer = random.randint(100, 400)
                if random.random() < 0.5: self.play_sound(self.walk_sound)

        if self.state == "IDLE":
            self.vx *= 0.8
        elif self.state == "WALK_LEFT":
            self.vx = (self.vx * 0.9) + (-self.walk_speed * 0.1)
        elif self.state == "WALK_RIGHT":
            self.vx = (self.vx * 0.9) + (self.walk_speed * 0.1)


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import ctypes
    myappid = 'jrhero.trickcal.chibi.godesktop.v2'  # String bebas, yang penting unik
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    app = QApplication(sys.argv)
    app_icon = QIcon(get_asset_path("logo/LogoIcon.ico"))
    app.setWindowIcon(app_icon)

    is_silent_mode = "--silent" in sys.argv
    saved_settings = load_config()

    final_settings = None

    if is_silent_mode and saved_settings:
        print("Running in Silent Mode (Startup)...")
        final_settings = saved_settings
    else:
        setup_dialog = SetupDialog(initial_settings=saved_settings)

        if setup_dialog.exec_() == QDialog.Accepted:
            final_settings = setup_dialog.get_settings()

            save_config(final_settings)

            try:
                AutoStartManager.toggle(final_settings["startup"])
            except Exception as e:
                print(f"Startup error: {e}")
        else:
            sys.exit()

    if final_settings:
        is_muted = not final_settings["sound"]
        allow_struggle = final_settings["struggle"]
        global_scale = final_settings["scale"]

        if final_settings["pumpkin"]:
            pumpkin = DesktopToy("characters/speaki/pumkin.png", size=80)
            global_pumpkin = pumpkin
            screen = app.primaryScreen().availableGeometry()

            pumpkin.move(screen.width() // 2, 0)
            pumpkin.show()
        else:
            global_pumpkin = None

        for _ in range(final_settings["count_speaki"]):
            spawn_pet("Speaki")

        for _ in range(final_settings["count_erpin"]):
            spawn_pet("Erpin")

        sys.exit(app.exec_())