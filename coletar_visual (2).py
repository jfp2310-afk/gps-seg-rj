#!/usr/bin/env python3
"""Coletor visual local de referências em capturas de mapas.

Abre uma imagem, permite clicar em símbolos e exporta coordenadas relativas
à imagem. Não gera coordenadas geográficas nem detecta territórios por GPS.

Uso: python coletar_visual.py captura.png --saida referencias_visuais.json
Requer Python 3 com tkinter (instalado em muitas distribuições desktop).
"""
import argparse
import json
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import simpledialog, messagebox

CATEGORIAS = ('CV', 'TCP', 'ADA', 'MILICIA', 'NEUTRA', 'OUTRA')


def executar(imagem: Path, saida: Path):
    janela = tk.Tk()
    janela.title('GPS JEAN SEG RJ - Coleta visual (sem GPS)')
    try:
        foto = tk.PhotoImage(file=str(imagem))
    except tk.TclError as exc:
        janela.destroy()
        raise SystemExit('Não foi possível abrir a imagem. Use PNG ou GIF. ' + str(exc))

    pontos = []
    barra = tk.Frame(janela)
    barra.pack(fill='x')
    info = tk.Label(barra, text='Clique no centro de cada legenda. Coordenadas são apenas da imagem.')
    info.pack(side='left', padx=8)

    canvas = tk.Canvas(janela, width=min(foto.width(), 1100), height=min(foto.height(), 700),
                       scrollregion=(0, 0, foto.width(), foto.height()))
    rolagem_x = tk.Scrollbar(janela, orient='horizontal', command=canvas.xview)
    rolagem_y = tk.Scrollbar(janela, orient='vertical', command=canvas.yview)
    canvas.configure(xscrollcommand=rolagem_x.set, yscrollcommand=rolagem_y.set)
    canvas.pack(side='left', fill='both', expand=True)
    rolagem_y.pack(side='right', fill='y')
    rolagem_x.pack(side='bottom', fill='x')
    canvas.create_image(0, 0, image=foto, anchor='nw')

    def clicar(event):
        x, y = round(canvas.canvasx(event.x)), round(canvas.canvasy(event.y))
        categoria = simpledialog.askstring('Legenda', 'Sigla: CV, TCP, ADA, MILICIA, NEUTRA ou OUTRA:', parent=janela)
        if not categoria:
            return
        categoria = categoria.strip().upper()
        if categoria not in CATEGORIAS:
            messagebox.showerror('Sigla inválida', 'Use uma das categorias informadas.')
            return
        nome = simpledialog.askstring('Nome', 'Nome da comunidade/local (se conhecido):', parent=janela)
        if nome is None:
            return
        item = {'id': len(pontos) + 1, 'categoria': categoria, 'nome': nome.strip(),
                'x_pixel': x, 'y_pixel': y,
                'x_relativo': round(x / foto.width(), 7),
                'y_relativo': round(y / foto.height(), 7)}
        pontos.append(item)
        canvas.create_oval(x-5, y-5, x+5, y+5, outline='yellow', width=2)
        canvas.create_text(x+9, y-9, text=str(item['id']), fill='yellow', anchor='w')
        info.configure(text=f'{len(pontos)} referência(s) marcada(s). Salve o JSON ao terminar.')

    def salvar():
        conteudo = {
            'formato': 'gps-jean-referencias-visuais-v1',
            'criado_em_utc': datetime.now(timezone.utc).isoformat(),
            'imagem': imagem.name,
            'largura': foto.width(), 'altura': foto.height(),
            'tipo_coordenadas': 'pixels_e_fracoes_da_imagem_sem_georreferenciamento',
            'apto_para_alerta_gps': False,
            'aviso': 'Pontos visuais não são polígonos ou coordenadas GPS.',
            'pontos': pontos,
        }
        saida.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding='utf-8')
        messagebox.showinfo('Concluído', f'{len(pontos)} pontos salvos em:\n{saida.resolve()}')

    canvas.bind('<Button-1>', clicar)
    tk.Button(barra, text='Salvar JSON', command=salvar).pack(side='right', padx=8)
    janela.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('imagem', type=Path, help='Captura do mapa em PNG/GIF')
    parser.add_argument('--saida', type=Path, default=Path('referencias_visuais.json'))
    args = parser.parse_args()
    if not args.imagem.is_file():
        parser.error('Imagem não encontrada: ' + str(args.imagem))
    executar(args.imagem, args.saida)


if __name__ == '__main__':
    main()
