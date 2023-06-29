from collections import defaultdict

from core.txt_file.logic import is_ring_closed


def process_feature_nodes(feature_nodes):
    # return [[completed_rings], [incomplete_rings, points]]
    if len(feature_nodes) < 3:
        return [[], [feature_nodes]]
    
    if feature_nodes[0]["sub_name"] is None:
        return [[], [feature_nodes]]
    else:
        rings = defaultdict(list)
        for node in feature_nodes:
            rings[node['sub_name']].append(node)

        return merge_rings(rings.values())


def merge_rings(rings):
    complete = []
    incomplete = []

    endpoints = {}

    for ring in rings:
        left = ring[0]
        left_id = left['id']
        
        right = ring[-1]
        right_id = right['id']

        if left_id in endpoints or right_id in endpoints:
            if right_id in endpoints and left_id not in endpoints:
                # Reverse this so it becomes a left connected ring
                # We can avoid duplicate code in 'right_id in endpoints' case
                ring = ring[::-1]
                
                left = ring[0]
                left_id = left['id']
                
                right = ring[-1]
                right_id = right['id']

            this_ring = endpoints.pop(left_id)
 
            if left_id == this_ring[-1]["id"]:
                this_ring = this_ring + ring[1:]
            else:
                this_ring = this_ring[::-1]
                this_ring = this_ring + ring[1:]

            if right_id in endpoints and not is_ring_closed(this_ring):
                right_ring = endpoints.pop(right_id)
                if right_id == right_ring[0]['id']:
                    this_ring = this_ring + right_ring[1:]
                else:
                    right_ring = right_ring[::-1]
                    this_ring = this_ring + right_ring[1:]

            if right_id in endpoints:
                endpoints.pop(right_id)

            endpoints[this_ring[-1]["id"]] = this_ring
            endpoints[this_ring[0]["id"]] = this_ring    
        else:
            endpoints[left_id] = ring
            endpoints[right_id] = ring

        endpoint_ids = list(endpoints.keys())
        for key in endpoint_ids:
            if endpoints[key][0]['id'] == endpoints[key][-1]['id']:
                complete.append(endpoints.pop(key))
                try:
                    del endpoints[endpoints[key][0]['id']]
                except:
                    pass
                try:
                    del endpoints[endpoints[key][-1]['id']]
                except:
                    pass
    
    endpoint_ids = list(endpoints.keys())
    written_ids = []
    for key in endpoint_ids:
        if key not in written_ids:
            written_ids.append(key)
            written_ids.append(endpoints[key][-1]['id'])
            
            incomplete.append(endpoints[key])
            endpoints.pop(endpoints[key][-1]['id'])

    return complete, incomplete
