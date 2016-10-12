from base64 import b64encode
from io import BytesIO

import pickle
with open('lp_simplex_theory.bin', 'rb') as f:
    lp_json_list_loaded = pickle.load(f)

for lp in lp_json_list_loaded:
    print lp
    selected_data_bytes = BytesIO ()
    pickle.dump (lp, selected_data_bytes)
    print b64encode(selected_data_bytes.getvalue()).decode()