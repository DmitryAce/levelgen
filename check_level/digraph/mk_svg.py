import graphviz

def create_svg_from_digraph(digraph_file_path, output_svg_path):
    # Чтение файла с digraph
    with open(digraph_file_path, 'r') as file:
        digraph_text = file.read()

    # Создание объекта Graph из текста digraph
    graph = graphviz.Source(digraph_text, format='svg')

    # Сохранение SVG в файл
    graph.render(output_svg_path, format='svg', cleanup=True)

    print(f"SVG успешно создан и сохранен в {output_svg_path}")



if __name__ == "__main__":
    digraph_file_path = "graph.txt"
    output_svg_path = "SVG"
    create_svg_from_digraph(digraph_file_path, output_svg_path)