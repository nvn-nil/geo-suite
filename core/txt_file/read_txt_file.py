from contextlib import contextmanager
from core.txt_file.logic import check_file_is_non_empty_txt_file, get_feature_name, get_node


@contextmanager
def read_txt_file(filepath):
    check_file_is_non_empty_txt_file(filepath)

    with open(filepath, "r") as fi:
        this_feature = None
        this_feature_nodes = []

        for line in fi:
            if not line.strip():
                continue

            if line.strip().lower().startswith("id"):
                continue
            
            line_items = line.strip().split("\t")

            feature_name, _ = get_feature_name(line_items[-1].strip())

            if not this_feature:
                this_feature = feature_name
                this_feature_nodes = [get_node(line_items)]
            elif this_feature != feature_name:
                # One group of items in the txt is fetched (excluding this node)
                yield this_feature_nodes
                
                # Start a new group with this iterations item
                this_feature = feature_name
                this_feature_nodes = [get_node(line_items)]
            else:
                this_feature_nodes.append(get_node(line_items))
