from PyQt5.QtWidgets import (
    QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem,
    QGraphicsTextItem, QVBoxLayout, QWidget, QLabel, QSplitter, QApplication
)
from PyQt5.QtGui import QBrush, QPen, QFont
from PyQt5.QtCore import Qt
import networkx as nx

class ZoomableGraphicsView(QGraphicsView):
    def wheelEvent(self, event):
        zoom_factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
        self.scale(zoom_factor, zoom_factor)

class GraphNavigator(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("Critical Thinking PyQt5 GUI")
        self.graph_model = model
        self.scene = QGraphicsScene()
        self.view = ZoomableGraphicsView(self.scene)
        self.details = QLabel("Click a node to view details")
        self.details.setWordWrap(True)
        self.details.setMinimumWidth(300)
        self.details.setFont(QFont("Arial", 10))
        layout = QSplitter(Qt.Horizontal)
        layout.addWidget(self.view)
        layout.addWidget(self.details)
        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.layout().addWidget(layout)
        self.setCentralWidget(container)
        self.node_items = {}
        self.display_graph()
        self.showMaximized()

    def display_graph(self, anchor_id=None, depth=1):
        self.scene.clear()
        G = self.graph_model.graph
        if anchor_id and anchor_id not in G:
            return
        subgraph = G if not anchor_id else self._get_subgraph(G, anchor_id, depth)
        pos = nx.spring_layout(subgraph, seed=42)
        scale = 300
        for node, (x, y) in pos.items():
            ellipse = QGraphicsEllipseItem(x*scale, y*scale, 60, 60)
            ellipse.setBrush(QBrush(Qt.green))
            ellipse.setPen(QPen(Qt.black, 2))
            ellipse.setData(0, node)
            ellipse.mousePressEvent = lambda event, n=node: self.on_node_click(n)
            self.scene.addItem(ellipse)
            label = QGraphicsTextItem(f"{node}")
            label.setPos(x*scale, y*scale)
            self.scene.addItem(label)
            self.node_items[node] = ellipse
        for u, v, data in subgraph.edges(data=True):
            self.scene.addLine(pos[u][0]*scale+30, pos[u][1]*scale+30, pos[v][0]*scale+30, pos[v][1]*scale+30, QPen(Qt.red, 2))
            label = self.scene.addText(data.get("type", ""))
            label.setPos((pos[u][0]+pos[v][0])*scale/2, (pos[u][1]+pos[v][1])*scale/2)

    def _get_subgraph(self, G, anchor_id, depth):
        visited, level = set(), {anchor_id: 0}
        queue = [anchor_id]
        while queue:
            node = queue.pop(0)
            visited.add(node)
            if level[node] < depth:
                for neighbor in G.successors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        level[neighbor] = level[node]+1
        return G.subgraph(visited)

    def on_node_click(self, node_id):
        node_data = self.graph_model.graph.nodes[node_id]
        content = node_data.get("content", "(No content)")
        ntype = node_data.get("type", "unknown")
        self.details.setText(f"Node: {node_id}\nType: {ntype}\n\n{content}")
        self.display_graph(anchor_id=node_id, depth=2)

def launch_gui(model):
    app = QApplication([])
    window = GraphNavigator(model)
    app.exec_()
