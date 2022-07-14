"""Tool for easy alignment of nuke nodes"""
from typing import List

import nuke


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
    rx = ref_node.knob("xpos").value()
    ry = ref_node.knob("ypos").value()
    rw = ref_node.screenWidth() / 2
    rh = ref_node.screenHeight() / 2

    for node in nodes:
        if not node:
            continue
        if node in run.touched:
            continue

        x = node.knob("xpos").value()
        y = node.knob("ypos").value()
        w = node.screenWidth() / 2
        h = node.screenHeight() / 2
        if x + w == rx + rw or y + h == ry + rh:
            # skip already aligned nodes
            pass
        elif difference(x, rx) < difference(y, ry):
            node.knob("xpos").setValue(rx + (rw - w))
        else:
            node.knob("ypos").setValue(ry + (rh - h))

        run.touched.append(node)
        next_nodes = [node.input(i) for i in range(node.inputs())]
        griddify(node, next_nodes)


def run():
    run.touched = []
    selected_nodes = nuke.selectedNodes()
    if not selected_nodes:
        pass
        return
    undo = nuke.Undo()
    undo.begin('Griddify')
    griddify(selected_nodes[0])
    undo.end()
