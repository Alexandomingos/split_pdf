🧠 Como funciona a lógica:
Durante a leitura das páginas:

Mantemos o nome e matrícula atuais em variáveis.

Se a próxima página tiver o mesmo nome e matrícula, ela é adicionada ao mesmo PDF.

Se for diferente, o PDF atual é salvo e um novo começa.

🆕 Código com essa lógica implementada:



✅ Comportamento do script:
Se houver 3 páginas com mesmo nome e matrícula, elas vão para o mesmo arquivo.

Ao detectar uma nova pessoa (nome ou matrícula diferentes), ele inicia um novo arquivo PDF.

Se quiser também agrupar mesmo que venham de arquivos PDF diferentes, posso adaptar o código pra isso! Deseja esse comportamento também?



✅ O que essa versão faz:
Percorre todos os PDFs, página por página.

Agrupa páginas por (nome, matrícula) em memória.

Ao final, salva um PDF para cada grupo único de nome e matrícula.

O CSV reflete todos os grupos criados.

🔧 Modificações feitas:
Adicionada extração da matrícula com matricula_match.

Nome do arquivo agora inclui matricula.

CSV também inclui a matrícula.

🛠 Como criar o .exe com PyInstaller
pyinstaller --onefile --windowed split_pdf_gui.py
Depois, o .exe estará em dist/split_pdf_gui.exe.
