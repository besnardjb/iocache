{
    "caches": {
        "burst" : {"bw": "1G", "size": "10G"},
        "storage" : {"bw": "500M", "size": "1T"},
        "lts" : {"bw": "200M", "size": "100T"}

    },
    "links": {
        "a_local": {"bw":"1G", "to": "burst"},
        "b_local": {"bw":"1G", "to": "burst"},
        "c_local": {"bw":"1G", "to": "burst"},
        "d_local": {"bw":"1G", "to": "burst"},
        "burst_stor": {"bw":"1G", "from": "burst", "to" : "storage"},
        "stor_lts": {"bw":"1G", "from": "storage", "to" : "lts"}

    }
}