import argparse
import json
import os
import yaml
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox


def verify_json(file_path):
    if not os.path.isfile(file_path):
        print(f"Błąd: Plik '{file_path}' nie istnieje.")
        return False

    try:
        with open(file_path, 'r') as file:
            json.load(file)
        print(f"Sukces: Plik '{file_path}' jest prawidłowym plikiem JSON.")
        return True
    except json.JSONDecodeError as e:
        print(f"Błąd: Plik '{file_path}' nie jest prawidłowym plikiem JSON. {e}")
        return False
    except Exception as e:
        print(f"Błąd: Wystąpił nieoczekiwany błąd podczas przetwarzania pliku '{file_path}'. {e}")
        return False


def verify_yml(file_path):
    if not os.path.isfile(file_path):
        print(f"Błąd: Plik '{file_path}' nie istnieje.")
        return False

    try:
        with open(file_path, 'r') as file:
            yaml.safe_load(file)
        print(f"Sukces: Plik '{file_path}' jest prawidłowym plikiem YAML.")
        return True
    except yaml.YAMLError as e:
        print(f"Błąd: Plik '{file_path}' nie jest prawidłowym plikiem YAML. {e}")
        return False
    except Exception as e:
        print(f"Błąd: Wystąpił nieoczekiwany błąd podczas przetwarzania pliku '{file_path}'. {e}")
        return False


def verify_xml(file_path):
    if not os.path.isfile(file_path):
        print(f"Błąd: Plik '{file_path}' nie istnieje.")
        return False

    try:
        tree = ET.parse(file_path)
        tree.getroot()
        print(f"Sukces: Plik '{file_path}' jest prawidłowym plikiem XML.")
        return True
    except ET.ParseError as e:
        print(f"Błąd: Plik '{file_path}' nie jest prawidłowym plikiem XML. {e}")
        return False
    except Exception as e:
        print(f"Błąd: Wystąpił nieoczekiwany błąd podczas przetwarzania pliku '{file_path}'. {e}")
        return False


def detect_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    return ext.lower()


def json_to_xml(data, root_name='root'):
    root = ET.Element(root_name)
    def build_tree(element, data):
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(element, key)
                build_tree(child, value)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(element, 'item')
                build_tree(child, item)
        else:
            element.text = str(data)
    build_tree(root, data)
    return root


def convert_file(input_path, output_path):
    input_type = detect_file_type(input_path)
    output_type = detect_file_type(output_path)

    if input_type not in ['.json', '.yml', '.yaml', '.xml']:
        print(f"Błąd: Nieobsługiwany typ pliku wejściowego '{input_type}'.")
        return False

    if output_type not in ['.json', '.yml', '.yaml', '.xml']:
        print(f"Błąd: Nieobsługiwany typ pliku wyjściowego '{output_type}'.")
        return False

    # Load the input file
    try:
        if input_type == '.json':
            with open(input_path, 'r') as file:
                data = json.load(file)
        elif input_type in ['.yml', '.yaml']:
            with open(input_path, 'r') as file:
                data = yaml.safe_load(file)
        elif input_type == '.xml':
            tree = ET.parse(input_path)
            data = tree.getroot()
    except Exception as e:
        print(f"Błąd: Nie udało się odczytać pliku wejściowego '{input_path}'. {e}")
        return False

    # Write to the output file
    try:
        if output_type == '.json':
            with open(output_path, 'w') as file:
                json.dump(data, file, indent=4)
        elif output_type in ['.yml', '.yaml']:
            with open(output_path, 'w') as file:
                yaml.dump(data, file, default_flow_style=False)
        elif output_type == '.xml':
            if isinstance(data, ET.Element):
                tree = ET.ElementTree(data)
            else:
                root = json_to_xml(data)
                tree = ET.ElementTree(root)
            tree.write(output_path)
    except Exception as e:
        print(f"Błąd: Nie udało się zapisać pliku wyjściowego '{output_path}'. {e}")
        return False

    print(f"Sukces: Przekonwertowano '{input_path}' na '{output_path}'.")
    return True


class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Konwerter Plików')

        layout = QVBoxLayout()

        self.input_label = QLabel('Wybierz plik wejściowy:')
        layout.addWidget(self.input_label)

        self.input_button = QPushButton('Przeglądaj...')
        self.input_button.clicked.connect(self.select_input_file)
        layout.addWidget(self.input_button)

        self.output_label = QLabel('Wybierz plik wyjściowy:')
        layout.addWidget(self.output_label)

        self.output_button = QPushButton('Przeglądaj...')
        self.output_button.clicked.connect(self.select_output_file)
        layout.addWidget(self.output_button)

        self.convert_button = QPushButton('Konwertuj')
        self.convert_button.clicked.connect(self.convert_files)
        layout.addWidget(self.convert_button)

        self.setLayout(layout)
        self.input_path = None
        self.output_path = None

    def select_input_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz plik wejściowy", "",
                                                   "Wszystkie pliki (*);;Pliki JSON (*.json);;Pliki YAML (*.yml *.yaml);;Pliki XML (*.xml)",
                                                   options=options)
        if file_path:
            self.input_path = file_path
            self.input_label.setText(f"Plik wejściowy: {file_path}")

    def select_output_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Wybierz plik wyjściowy", "",
                                                   "Pliki JSON (*.json);;Pliki YAML (*.yml *.yaml);;Pliki XML (*.xml)",
                                                   options=options)
        if file_path:
            self.output_path = file_path
            self.output_label.setText(f"Plik wyjściowy: {file_path}")

    def convert_files(self):
        if not self.input_path or not self.output_path:
            QMessageBox.warning(self, "Ostrzeżenie", "Proszę wybrać zarówno plik wejściowy, jak i wyjściowy.")
            return

        input_type = detect_file_type(self.input_path)
        if input_type == '.json':
            if not verify_json(self.input_path):
                QMessageBox.critical(self, "Błąd", "Nieprawidłowy plik JSON.")
                return
        elif input_type in ['.yml', '.yaml']:
            if not verify_yml(self.input_path):
                QMessageBox.critical(self, "Błąd", "Nieprawidłowy plik YAML.")
                return
        elif input_type == '.xml':
            if not verify_xml(self.input_path):
                QMessageBox.critical(self, "Błąd", "Nieprawidłowy plik XML.")
                return
        else:
            QMessageBox.critical(self, "Błąd", f"Nieobsługiwany typ pliku wejściowego: {input_type}")
            return

        if convert_file(self.input_path, self.output_path):
            QMessageBox.information(self, "Sukces", "Plik został pomyślnie przekonwertowany.")
        else:
            QMessageBox.critical(self, "Błąd", "Nie udało się przekonwertować pliku.")


def main():
    parser = argparse.ArgumentParser(description='Weryfikuj i konwertuj pliki JSON, YAML lub XML.')
    parser.add_argument('--verify-json', type=str, help='Ścieżka do pliku JSON do weryfikacji.')
    parser.add_argument('--verify-yml', type=str, help='Ścieżka do pliku YAML do weryfikacji.')
    parser.add_argument('--verify-xml', type=str, help='Ścieżka do pliku XML do weryfikacji.')
    parser.add_argument('--convert', nargs=2, help='Konwertuj plik1 na plik2. Wykrywa typy plików na podstawie rozszerzenia.')

    args = parser.parse_args()

    if args.verify_json:
        verify_json(args.verify)