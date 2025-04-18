import sys
import os
import fitz  # PyMuPDF
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt
import re
import unicodedata

class PDFSplitter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Separador de PDF com Renomeação Inteligente")
        self.setFixedSize(550, 280)
        self.pdf_paths = []
        self.output_dir = ""

        layout = QVBoxLayout()

        self.label_pdf = QLabel("📄 Nenhum PDF selecionado")
        layout.addWidget(self.label_pdf)

        btn_pdf = QPushButton("Selecionar PDF(s)")
        btn_pdf.clicked.connect(self.select_pdfs)
        layout.addWidget(btn_pdf)

        self.label_output = QLabel("📁 Nenhuma pasta de destino selecionada")
        layout.addWidget(self.label_output)

        btn_output = QPushButton("Selecionar Pasta de Destino")
        btn_output.clicked.connect(self.select_output_dir)
        layout.addWidget(btn_output)

        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress)

        btn_split = QPushButton("Separar PDF e Renomear")
        btn_split.clicked.connect(self.split_pdfs)
        layout.addWidget(btn_split)

        self.setLayout(layout)

    def select_pdfs(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Selecione um ou mais PDFs", "", "PDF Files (*.pdf)")
        if paths:
            self.pdf_paths = paths
            self.label_pdf.setText(f"📄 {len(paths)} arquivo(s) selecionado(s)")

    def select_output_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Selecione a pasta de destino")
        if path:
            self.output_dir = path
            self.label_output.setText(f"📁 {path}")

    def limpar_nome(self, texto):
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
        texto = re.sub(r'[^A-Za-z0-9_-]', '_', texto)
        return texto[:150]

    def extract_info(self, text):
        nome_match = re.search(r"Eu, ([A-Za-zÀ-ÿ0-9 ]+)", text)
        matricula_match = re.search(r"matricula (\d+)", text, re.IGNORECASE)
        data_match = re.search(r"\b(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})", text)

        nome = nome_match.group(1).strip().replace(" ", "_") if nome_match else "desconhecido"
        matricula = matricula_match.group(1) if matricula_match else "sem_matricula"
        data = data_match.group(1) if data_match else "0000-00-00"
        hora = data_match.group(2).replace(":", "-") if data_match else "00-00"

        if "/" in data:
            partes = data.split("/")
            data_formatada = f"{partes[2]}-{partes[1]}-{partes[0]}"
        else:
            data_formatada = data

        # Descrição ignorada (não será mais usada)
        return nome, matricula, data_formatada, hora, ""

    def split_pdfs(self):
        if not self.pdf_paths or not self.output_dir:
            QMessageBox.warning(self, "Aviso", "Selecione ao menos um PDF e uma pasta de destino.")
            return

        csv_path = os.path.join(self.output_dir, "resumo_das_paginas.csv")
        registros = []

        try:
            total_paginas = sum(len(fitz.open(p)) for p in self.pdf_paths)
            self.progress.setMaximum(total_paginas)
            self.progress.setValue(0)
            pagina_global = 0

            # Agrupamento por (nome, matrícula)
            grupos = {}

            for pdf_path in self.pdf_paths:
                doc = fitz.open(pdf_path)

                for i in range(len(doc)):
                    page = doc.load_page(i)
                    text = page.get_text()

                    nome, matricula, data, hora, _ = self.extract_info(text)
                    chave = (nome, matricula)

                    if chave not in grupos:
                        grupos[chave] = {
                            "pdf": fitz.open(),
                            "datas": [],
                            "total_paginas": 0
                        }

                    grupos[chave]["pdf"].insert_pdf(doc, from_page=i, to_page=i)
                    grupos[chave]["datas"].append(data)
                    grupos[chave]["total_paginas"] += 1
                    pagina_global += 1
                    self.progress.setValue(pagina_global)

            for (nome, matricula), info in grupos.items():
                nome_limp = self.limpar_nome(nome)
                matricula_limp = self.limpar_nome(matricula)

                datas_ordenadas = sorted(info["datas"])
                data_inicio = datas_ordenadas[0]
                data_fim = datas_ordenadas[-1]

                nome_arquivo = f"{nome_limp}__{matricula_limp}__{data_inicio}_a_{data_fim}.pdf"
                output_path = os.path.join(self.output_dir, nome_arquivo)

                info["pdf"].save(output_path)
                info["pdf"].close()

                registros.append([
                    nome.replace("_", " "),
                    matricula,
                    data_inicio,
                    data_fim,
                    info["total_paginas"],
                    nome_arquivo
                ])

            with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Nome", "Matrícula", "Data Início", "Data Fim", "Total de Páginas", "Arquivo"])
                writer.writerows(registros)

            QMessageBox.information(self, "Concluído", f"{pagina_global} páginas processadas.\nCSV salvo como 'resumo_das_paginas.csv'.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFSplitter()
    window.show()
    sys.exit(app.exec_())
