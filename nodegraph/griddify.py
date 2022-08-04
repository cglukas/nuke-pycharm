"""Tool for easy alignment of nuke nodes"""
import dataclasses
from typing import List, Union

import nuke

@dataclasses.dataclass
class Vector:
    x: Union[int, float]
    y: Union[int, float]

    def __len__(self):
        difference(self.x, self.y)


MIN_DIST = Vector(60, 30)

def difference(x1, x2):
    """Calculate the difference between two numbers"""
    if x1 > x2:
        return x1 - x2
    return x2 - x1


def griddify(ref_node: nuke.Node, nodes: List[nuke.Node] = []):
    """Align all nodes to the reference node

    Args:
        ref_node: reference node to align other nodes to
        nodes: connected nodes to align
    """
    nodes = nodes or [ref_node.input(i) for i in range(ref_node.inputs())]
    rx = ref_node.xpos()
    ry = ref_node.ypos()
    rw = ref_node.screenWidth() / 2
    rh = ref_node.screenHeight() / 2

    for index, node in enumerate(nodes):
        if not node:
            continue
        if node in run.touched:
            continue

        x = node.xpos()
        y = node.ypos()
        w = node.screenWidth() / 2
        h = node.screenHeight() / 2
        len_y = difference(y, ry)
        len_x = difference(x, rx)
        only_vertical = index == 0 and node.Class() != "Dot"
        if x + w == rx + rw or y + h == ry + rh:
            # skip already aligned nodes
            pass
        elif len_x < len_y or only_vertical:
            node.setXpos(int(rx + (rw - w)))
            if len_y < MIN_DIST.y:
                node.setYpos(node.ypos() - MIN_DIST.y)
        else:
            node.setYpos(int(ry + (rh - h)))
            if len_x < MIN_DIST.x:
                node.setXpos(node.xpos() + MIN_DIST.x)

        run.touched.append(node)
        next_nodes = [node.input(i) for i in range(node.inputs())]
        griddify(node, next_nodes)


def run():
    run.touched = []
    selected_nodes = nuke.selectedNodes()
    if not selected_nodes:
        return
    undo = nuke.Undo()
    undo.begin('Griddify')
    griddify(selected_nodes[0])
    undo.end()
